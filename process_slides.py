# ----------------------------------------------------------------------
# 1. ---- CONFIGURATION (!!! YOU MUST CHANGE THESE VALUES !!!) ----
# ----------------------------------------------------------------------
import os
import glob
import re
import time
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

# ----------------------------------------------------------------------
# 2. ---- HELPER FUNCTIONS ----
# ----------------------------------------------------------------------

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

# ----------------------------------------------------------------------
# 4. ---- INITIALIZE AZURE CLIENT ----
# ----------------------------------------------------------------------
# Create an authenticated Image Analysis client
try:
    client = ImageAnalysisClient(
        endpoint=AZURE_ENDPOINT,
        credential=AzureKeyCredential(AZURE_KEY)
    )
    print("Azure AI Vision client initialized successfully.")
except Exception as e:
    print(f"Error initializing Azure client: {e}")
    print("Please check your AZURE_ENDPOINT and AZURE_KEY values.")
    exit()

# ----------------------------------------------------------------------
# 5. ---- PROCESS IMAGES ----
# ----------------------------------------------------------------------
# Find all .png and .jpg images in the specified folder
image_files = sorted(glob.glob(os.path.join(IMAGE_FOLDER_PATH, "*.png")) + glob.glob(os.path.join(IMAGE_FOLDER_PATH, "*.jpg")))

if not image_files:
    print(f"Error: No .png or .jpg files found in '{IMAGE_FOLDER_PATH}'.")
    print("Please check your IMAGE_FOLDER_PATH setting.")
    exit()

print(f"Found {len(image_files)} images to process. Starting analysis...")

# Loop through each file with a progress bar
for image_path in tqdm(image_files, desc="Processing Images"):
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
            
            # Success - break out of retry loop
            break
            
        except (ConnectionResetError, ConnectionError, OSError) as e:
            # Handle connection-related errors with retry logic
            if attempt < max_retries - 1:
                print(f"\n[Retry {attempt + 1}/{max_retries}] Connection error for {os.path.basename(image_path)}, retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                print(f"\n[Failed] Could not process {os.path.basename(image_path)} after {max_retries} attempts")
        except Exception as e:
            # Handle other errors without retry
            if "Connection" in str(e) or "connection" in str(e):
                # It's a wrapped connection error
                if attempt < max_retries - 1:
                    print(f"\n[Retry {attempt + 1}/{max_retries}] Network error for {os.path.basename(image_path)}, retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                else:
                    print(f"\n[Failed] Could not process {os.path.basename(image_path)} after {max_retries} attempts")
            else:
                # Other errors - don't retry
                print(f"\n[Error] Processing {os.path.basename(image_path)}: {e}")
                break

print("\nImage processing complete.")
print(f"Found {len(slide_order)} unique slides.")

# ----------------------------------------------------------------------
# 6. ---- WRITE OUTPUT FILE ----
# ----------------------------------------------------------------------
print(f"Writing notes to '{OUTPUT_FILE}'...")

try:
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
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

    print("Processing complete. Your course notes are ready!")
except Exception as e:
    print(f"Error writing output file: {e}")
