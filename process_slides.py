# ----------------------------------------------------------------------
# 1. ---- CONFIGURATION (!!! YOU MUST CHANGE THESE VALUES !!!) ----
# ----------------------------------------------------------------------
import os
import glob
import re
import time
import json
import logging
from datetime import datetime
from tqdm import tqdm
from dotenv import load_dotenv
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential

# Load environment variables from a .env file
load_dotenv()

# --- Configuration (all loaded from .env file) ---
# All configuration values are now in the .env file for easy management
AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
AZURE_KEY = os.getenv("AZURE_KEY")
IMAGE_FOLDER_PATH = os.getenv("IMAGE_FOLDER_PATH")
OUTPUT_FILE_NAME = os.getenv("OUTPUT_FILE", "Notes.md")  # Default: Notes.md
CAPTION_SEPARATOR_Y_PIXEL = int(os.getenv("CAPTION_SEPARATOR_Y_PIXEL", "850"))  # Default: 850

# Ensure output file is saved in the script's directory, not the working directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(SCRIPT_DIR, OUTPUT_FILE_NAME)
PROCESSED_CACHE_FILE = os.path.join(SCRIPT_DIR, ".processed_images.json")
LOG_FILE = os.path.join(SCRIPT_DIR, "processing.log")

# --- Setup Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Suppress Azure SDK verbose logging (only show warnings and errors)
logging.getLogger('azure').setLevel(logging.WARNING)
logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.WARNING)

# ----------------------------------------------------------------------
# 2. ---- HELPER FUNCTIONS ----
# ----------------------------------------------------------------------

def load_processed_cache():
    """Load the cache of already processed images."""
    if os.path.exists(PROCESSED_CACHE_FILE):
        try:
            with open(PROCESSED_CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load cache file: {e}")
            return {}
    return {}

def save_processed_cache(cache):
    """Save the cache of processed images."""
    try:
        with open(PROCESSED_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Could not save cache file: {e}")

def get_file_info(file_path):
    """Get file metadata (size, creation time, modification time)."""
    stat = os.stat(file_path)
    return {
        'size': stat.st_size,
        'created': stat.st_ctime,
        'modified': stat.st_mtime
    }

def format_file_size(size_bytes):
    """Convert bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def _format_text_with_structure(lines):
    """
    Format a list of text lines while preserving structure like bullet points,
    numbered lists, and paragraphs.
    
    Args:
        lines: List of text strings from OCR
        
    Returns:
        Formatted text string with proper line breaks
    """
    if not lines:
        return ""
    
    formatted_lines = []
    
    # Patterns to detect list items
    bullet_pattern = re.compile(r'^[\*\-\•\◦\▪\►\→]\s*')
    number_pattern = re.compile(r'^\d+[\.\)]\s+')
    letter_pattern = re.compile(r'^[a-zA-Z][\.\)]\s+')
    
    for i, line in enumerate(lines):
        text = line.strip()
        if not text:
            continue
            
        # Check if this line is a bullet point
        if bullet_pattern.match(text):
            formatted_lines.append(text)
            
        # Check if this line is a numbered list item
        elif number_pattern.match(text):
            formatted_lines.append(text)
            
        # Check if this line is a lettered list item (a., b., etc.)
        elif letter_pattern.match(text):
            formatted_lines.append(text)
            
        # Check if the line looks like a heading (ALL CAPS or Title Case with short length)
        elif len(text) < 50 and (text.isupper() or text.istitle()):
            # Add extra line break before headings (except first line)
            if formatted_lines:
                formatted_lines.append("")
            formatted_lines.append(text)
            
        # Regular paragraph text
        else:
            # If previous line exists and looks like it continues (lowercase start, no punctuation end)
            if (formatted_lines and 
                not bullet_pattern.match(lines[i-1].strip()) and
                not number_pattern.match(lines[i-1].strip()) and
                formatted_lines[-1] and
                not formatted_lines[-1].endswith(('.', '!', '?', ':')) and
                text[0].islower()):
                # Continue the previous line
                formatted_lines[-1] += " " + text
            else:
                formatted_lines.append(text)
    
    # Join lines with newlines to preserve structure
    return "\n".join(formatted_lines).strip()

# ----------------------------------------------------------------------
# 3. ---- SCRIPT INITIALIZATION ----
# ----------------------------------------------------------------------

# This dictionary will store our final, grouped data
# Key: The main text of a slide
# Value: A list of all unique captions found for that slide
grouped_slides = {}

# This list maintains the original order of the unique slides as they appear
slide_order = []

# Dictionary to store slide data by image filename for caching
image_to_slide_map = {}

# ----------------------------------------------------------------------
# 4. ---- INITIALIZE AZURE CLIENT ----
# ----------------------------------------------------------------------
logger.info("=" * 60)
logger.info("Starting Slide Text Extractor")
logger.info("=" * 60)

# Create an authenticated Image Analysis client
try:
    client = ImageAnalysisClient(
        endpoint=AZURE_ENDPOINT,
        credential=AzureKeyCredential(AZURE_KEY)
    )
    logger.info("Azure AI Vision client initialized successfully")
except Exception as e:
    logger.error(f"Error initializing Azure client: {e}")
    logger.error("Please check your AZURE_ENDPOINT and AZURE_KEY values")
    exit()

# ----------------------------------------------------------------------
# 5. ---- PROCESS IMAGES ----
# ----------------------------------------------------------------------
# Load cache of previously processed images
processed_cache = load_processed_cache()
logger.info(f"Loaded cache with {len(processed_cache)} previously processed images")

# Find all .png and .jpg images in the specified folder
image_files = glob.glob(os.path.join(IMAGE_FOLDER_PATH, "*.png")) + glob.glob(os.path.join(IMAGE_FOLDER_PATH, "*.jpg"))

if not image_files:
    logger.error(f"No .png or .jpg files found in '{IMAGE_FOLDER_PATH}'")
    logger.error("Please check your IMAGE_FOLDER_PATH setting")
    exit()

# Sort images by creation date (oldest first) to maintain lecture order
image_files_with_dates = [(f, os.path.getctime(f)) for f in image_files]
image_files_with_dates.sort(key=lambda x: x[1])  # Sort by creation time
image_files = [f[0] for f in image_files_with_dates]

# Calculate total size
total_size = sum(os.path.getsize(f) for f in image_files)
logger.info(f"Found {len(image_files)} images ({format_file_size(total_size)} total)")
logger.info(f"Images sorted by creation date (maintaining lecture order)")

# Track processing statistics
stats = {
    'total': len(image_files),
    'processed': 0,
    'skipped': 0,
    'failed': 0,
    'start_time': time.time()
}

# Loop through each file with a progress bar
for image_path in tqdm(image_files, desc="Processing Images"):
    file_name = os.path.basename(image_path)
    file_info = get_file_info(image_path)
    
    # Check if this file was already processed (same name and size)
    if file_name in processed_cache:
        cached_info = processed_cache[file_name]
        if cached_info.get('size') == file_info['size'] and cached_info.get('modified') == file_info['modified']:
            # Load the cached slide data
            if 'slide_text' in cached_info and 'caption_text' in cached_info:
                slide_text = cached_info['slide_text']
                caption_text = cached_info['caption_text']
                
                # Re-populate grouped_slides and slide_order from cache
                if slide_text:
                    if slide_text not in grouped_slides:
                        grouped_slides[slide_text] = []
                        slide_order.append(slide_text)
                    if caption_text and caption_text not in grouped_slides[slide_text]:
                        grouped_slides[slide_text].append(caption_text)
                
                logger.debug(f"Loaded cached data for: {file_name}")
                stats['skipped'] += 1
                continue
            else:
                # Old cache format without slide data - need to reprocess
                logger.debug(f"Cache missing slide data for {file_name}, will reprocess")
        else:
            logger.debug(f"File modified since last cache: {file_name}")
    
    # Retry logic for Azure API connection issues
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            # Open the image file in binary read mode
            with open(image_path, "rb") as f:
                image_data = f.read()

            # Call the Azure AI Vision service to extract text
            result = client.analyze(
                image_data=image_data,
                visual_features=[VisualFeatures.READ]
            )

            # Prepare lists to hold text from different parts of the slide
            slide_text_lines = []
            caption_text_lines = []

            if result.read is not None and result.read.blocks:
                # Collect all lines from all blocks
                all_lines = []
                for block in result.read.blocks:
                    if block.lines:
                        all_lines.extend(block.lines)
                
                # Sort lines by their vertical position to ensure correct order
                sorted_lines = sorted(all_lines, key=lambda line: line.bounding_polygon[0].y)
                
                for line in sorted_lines:
                    # If the line's starting Y-position is above the separator, it's slide content
                    if line.bounding_polygon[0].y < CAPTION_SEPARATOR_Y_PIXEL:
                        slide_text_lines.append(line.text)
                    # Otherwise, it's part of the caption
                    else:
                        caption_text_lines.append(line.text)

            # Format text with proper line breaks and structure preservation
            slide_text = _format_text_with_structure(slide_text_lines)
            caption_text = _format_text_with_structure(caption_text_lines)

            # --- Grouping Logic ---
            if slide_text: # Only process if the main slide text is not empty
                # If this is the first time we've seen this slide text...
                if slide_text not in grouped_slides:
                    grouped_slides[slide_text] = []  # Create a new entry for it
                    slide_order.append(slide_text)   # Add it to the ordered list

                # If the caption is not blank and we haven't stored this caption before...
                if caption_text and caption_text not in grouped_slides[slide_text]:
                    grouped_slides[slide_text].append(caption_text)
            
            # Mark this file as successfully processed and store slide data in cache
            processed_cache[file_name] = {
                **file_info,
                'slide_text': slide_text,
                'caption_text': caption_text
            }
            stats['processed'] += 1
            logger.debug(f"Successfully processed: {file_name}")
            
            # Success - break out of retry loop
            break
            
        except (ConnectionResetError, ConnectionError, OSError) as e:
            # Handle connection-related errors with retry logic
            if attempt < max_retries - 1:
                logger.warning(f"[Retry {attempt + 1}/{max_retries}] Connection error for {file_name}, retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                logger.error(f"[Failed] Could not process {file_name} after {max_retries} attempts")
                stats['failed'] += 1
        except Exception as e:
            # Handle other errors without retry
            if "Connection" in str(e) or "connection" in str(e):
                # It's a wrapped connection error
                if attempt < max_retries - 1:
                    logger.warning(f"[Retry {attempt + 1}/{max_retries}] Network error for {file_name}, retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                else:
                    logger.error(f"[Failed] Could not process {file_name} after {max_retries} attempts")
                    stats['failed'] += 1
            else:
                # Other errors - don't retry
                logger.error(f"[Error] Processing {file_name}: {e}")
                stats['failed'] += 1
                break

# Save the processed files cache
save_processed_cache(processed_cache)

# Calculate processing time
stats['end_time'] = time.time()
stats['total_time'] = stats['end_time'] - stats['start_time']

# Log final statistics
logger.info("=" * 60)
logger.info("Processing Complete!")
logger.info("=" * 60)
logger.info(f"Total images found: {stats['total']}")
logger.info(f"Successfully processed: {stats['processed']}")
logger.info(f"Skipped (already processed): {stats['skipped']}")
logger.info(f"Failed: {stats['failed']}")
logger.info(f"Unique slides extracted: {len(slide_order)}")
logger.info(f"Total processing time: {stats['total_time']:.2f} seconds")
if stats['processed'] > 0:
    logger.info(f"Average time per image: {stats['total_time'] / stats['processed']:.2f} seconds")
logger.info("=" * 60)

# ----------------------------------------------------------------------
# 6. ---- WRITE OUTPUT FILE ----
# ----------------------------------------------------------------------
logger.info(f"Writing notes to '{OUTPUT_FILE}'...")

try:
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        # Write header with metadata
        f.write(f"# Course Notes\n\n")
        f.write(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
        f.write(f"*Total slides: {len(slide_order)}*\n\n")
        f.write(f"---\n\n")
        
        # Loop through the unique slides in the order they were first seen
        for i, slide_text in enumerate(slide_order):
            # Write the slide number as a Markdown heading
            f.write(f"## Slide {i + 1}\n\n")

            # Write the main slide text (preserve formatting with line breaks)
            # Split by newlines to handle multi-line formatted content
            slide_lines = slide_text.split('\n')
            for line in slide_lines:
                if line.strip():
                    f.write(f"> {line}\n")
            f.write("\n")

            # Write all the unique captions found for this slide
            captions = grouped_slides[slide_text]
            if captions:
                f.write("### Captions:\n\n")
                for caption in sorted(captions):
                    # Preserve formatting in captions too
                    caption_lines = caption.split('\n')
                    for cap_line in caption_lines:
                        if cap_line.strip():
                            f.write(f"* {cap_line}\n")
                f.write("\n")

            # Write a horizontal rule to separate the slides
            f.write("---\n\n")

    logger.info(f"Successfully wrote {len(slide_order)} slides to output file")
    logger.info("Processing complete. Your course notes are ready!")
    print(f"\n[SUCCESS] Generated '{os.path.basename(OUTPUT_FILE)}' with {len(slide_order)} slides")
    print(f"[INFO] Check 'processing.log' for detailed information")
except Exception as e:
    logger.error(f"Error writing output file: {e}")
    print(f"[ERROR] Error writing output file: {e}")
