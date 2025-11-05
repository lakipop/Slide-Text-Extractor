# ----------------------------------------------------------------------
# 1. ---- CONFIGURATION (!!! YOU MUST CHANGE THESE VALUES !!!) ----
# ----------------------------------------------------------------------
import os
import glob
from tqdm import tqdm
from dotenv import load_dotenv
from azure.ai.vision.imageanalysis import ImageAnalysisClient, VisualFeatures
from azure.core.credentials import AzureKeyCredential

# Load environment variables from a .env file
load_dotenv()

# --- Secure Configuration (loaded from .env file) ---
# Your Azure credentials are now loaded securely from the .env file
AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
AZURE_KEY = os.getenv("AZURE_KEY")

# --- Local Configuration (edit these values directly) ---
# Point this to the folder containing your 1500+ screenshots
# IMPORTANT: Use 'r' before the string to handle backslashes correctly
IMAGE_FOLDER_PATH = r"C:\Users\lakin\Desktop\MyScreenshots"

# The name of the final output file
OUTPUT_FILE = "course_notes.md"

# The vertical pixel line to separate slide text from the caption below it.
# Any text starting *below* this Y-coordinate will be treated as a caption.
# You WILL need to adjust this by examining the screenshots. See GUIDE.md for details.
CAPTION_SEPARATOR_Y_PIXEL = 850

# ----------------------------------------------------------------------
# 2. ---- SCRIPT INITIALIZATION ----
# ----------------------------------------------------------------------

# This dictionary will store our final, grouped data
# Key: The main text of a slide
# Value: A list of all unique captions found for that slide
grouped_slides = {}

# This list maintains the original order of the unique slides as they appear
slide_order = []

# ----------------------------------------------------------------------
# 3. ---- INITIALIZE AZURE CLIENT ----
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
# 4. ---- PROCESS IMAGES ----
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

        if result.read is not None:
            # Sort lines by their vertical position to ensure correct order
            sorted_lines = sorted(result.read.lines, key=lambda line: line.bounding_polygon[0].y)
            
            for line in sorted_lines:
                # If the line's starting Y-position is above the separator, it's slide content
                if line.bounding_polygon[0].y < CAPTION_SEPARATOR_Y_PIXEL:
                    slide_text_lines.append(line.text)
                # Otherwise, it's part of the caption
                else:
                    caption_text_lines.append(line.text)

        # Join the lines into single strings
        slide_text = " ".join(slide_text_lines).strip()
        caption_text = " ".join(caption_text_lines).strip()

        # --- Grouping Logic ---
        if slide_text: # Only process if the main slide text is not empty
            # If this is the first time we've seen this slide text...
            if slide_text not in grouped_slides:
                grouped_slides[slide_text] = []  # Create a new entry for it
                slide_order.append(slide_text)   # Add it to the ordered list

            # If the caption is not blank and we haven't stored this caption before...
            if caption_text and caption_text not in grouped_slides[slide_text]:
                grouped_slides[slide_text].append(caption_text)

    except Exception as e:
        print(f"\nAn error occurred while processing {os.path.basename(image_path)}: {e}")

print("\nImage processing complete.")
print(f"Found {len(slide_order)} unique slides.")

# ----------------------------------------------------------------------
# 5. ---- WRITE OUTPUT FILE ----
# ----------------------------------------------------------------------
print(f"Writing notes to '{OUTPUT_FILE}'...")

try:
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        # Loop through the unique slides in the order they were first seen
        for i, slide_text in enumerate(slide_order):
            # Write the slide number as a Markdown heading
            f.write(f"## Slide {i + 1}\n\n")

            # Write the main slide text in a blockquote
            f.write(f"> {slide_text}\n\n")

            # Write all the unique captions found for this slide
            captions = grouped_slides[slide_text]
            if captions:
                f.write("### Captions:\n")
                for caption in sorted(captions): # Sort captions for consistency
                    f.write(f"* {caption}\n")
                f.write("\n")

            # Write a horizontal rule to separate the slides
            f.write("---\n\n")

    print("Processing complete. Your course notes are ready!")
except Exception as e:
    print(f"Error writing output file: {e}")
