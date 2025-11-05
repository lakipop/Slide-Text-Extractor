# Slide Text Extractor

This project uses Azure AI Vision to process a large number of course screenshots, de-duplicate them based on their visual text content, and merge all unique captions into a single, ordered Markdown document.

---

### 1. Azure Setup

1. Go to the [Azure Portal](https://portal.azure.com/).
2. Create a new **"Azure AI Services"** resource.
3. Once created, navigate to the resource's **"Keys and Endpoint"** blade.
4. Copy the `KEY 1` and `ENDPOINT` values. You will need these for the script.

### 2. Local Setup

1. Clone this repository to your local machine.
2. Open a terminal in the project directory.
3. Create a Python virtual environment:
    ```bash
    python -m venv venv
    ```
4. Activate the virtual environment:
    * **Windows (PowerShell/CMD):** `.\venv\Scripts\activate`
    * **macOS/Linux (bash):** `source venv/bin/activate`

### 3. Install Dependencies

With your virtual environment active, install the required Python packages:

```bash
pip install -r requirements.txt
```

### 4. Configure the Script

1. Open the `process_slides.py` file in a code editor.
2. Fill in the 5 configuration variables at the top of the file:
    * `AZURE_ENDPOINT`: Your endpoint URL from the Azure portal.
    * `AZURE_KEY`: Your key from the Azure portal.
    * `IMAGE_FOLDER_PATH`: The absolute path to the folder containing your screenshots.
    * `OUTPUT_FILE`: The desired name for your notes file (default is `course_notes.md`).
    * `CAPTION_SEPARATOR_Y_PIXEL`: **(Crucial!)** This integer determines where the slide content ends and the caption begins. You must inspect your screenshots to find a suitable Y-pixel value that separates the two regions.

### 5. Run the Script

Once configured, run the script from your terminal:

```bash
python process_slides.py
```

The script will process all images and generate the specified output file in the project directory.
