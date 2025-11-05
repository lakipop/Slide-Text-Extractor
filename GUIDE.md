# Full Guide: Slide Text Extractor

This guide provides a detailed, step-by-step walkthrough for setting up and using the Slide Text Extractor project.

---

### Part 1: Create the Azure AI Resource

To use this script, you need an Azure account and an "Azure AI Services" resource. This service will perform the Optical Character Recognition (OCR) to read text from your images.

1.  **Navigate to the Azure Portal:** Go to [portal.azure.com](https://portal.azure.com/) and sign in.
2.  **Create a Resource:**
    *   Click the **"+ Create a resource"** button.
    *   In the search bar, type **"Azure AI services"** and select it.
    *   Click **"Create"**.
3.  **Configure the Resource:**
    *   **Subscription:** Choose your Azure subscription.
    *   **Resource group:** Create a new one (e.g., `AIServices-RG`) or select an existing one.
    *   **Region:** Choose a region close to you (e.g., `East US`).
    *   **Name:** Give your resource a unique name (e.g., `MyCourseOCR`).
    *   **Pricing tier:** Select **`Free F0`** for free usage within generous limits.
    *   Check the "I have read and understand..." box.
4.  **Review and Create:** Click **"Review + create"**, then **"Create"**. Wait for the deployment to complete.
5.  **Get Your Keys and Endpoint:**
    *   Once deployed, click **"Go to resource"**.
    *   In the left-hand menu, under "Resource Management", click **"Keys and Endpoint"**.
    *   You will see two keys and an endpoint URL. You need **`KEY 1`** and the **`Endpoint`**.
    *   **Keep this page open!** You will need these values in the next section.

---

### Part 2: Set Up Your Local Project

Now, let's set up the project on your computer and configure all settings in one place.

1.  **Clone the Repository:** If you haven't already, clone this project to your machine.
2.  **Create Your `.env` File:**
    *   In the project folder, find the file named `.env.example`.
    *   **Rename** this file to just `.env`.
3.  **Configure All Settings in `.env`:**
    *   Open the new `.env` file in a text editor.
    *   **Azure Credentials:**
        *   Copy your **`Endpoint`** URL from the Azure portal and paste it as the value for `AZURE_ENDPOINT`.
        *   Copy your **`KEY 1`** from the Azure portal and paste it as the value for `AZURE_KEY`.
    *   **Image Folder Path:**
        *   Update `IMAGE_FOLDER_PATH` with the full path to your screenshots folder.
        *   **Important:** Use forward slashes (`/`) or double backslashes (`\\`) in Windows paths.
        *   Example: `C:/Users/MyUser/Desktop/MyScreenshots`
    *   **Output File Name:**
        *   Change `OUTPUT_FILE` if you want a different name (default is `course_notes.md`).
    *   **Caption Separator:**
        *   Update `CAPTION_SEPARATOR_Y_PIXEL` with the correct Y-pixel value (see Part 4 below).
    *   Save and close the file. The `.gitignore` file prevents this file from being uploaded to Git.

---

### Part 3: Install Dependencies

1.  **Open a Terminal:** Open a terminal or command prompt inside the project's root directory.
2.  **Create a Virtual Environment:** This creates an isolated environment for the project's Python packages.
    ```bash
    python -m venv venv
    ```
3.  **Activate the Environment:**
    *   **Windows (PowerShell/CMD):** `.\venv\Scripts\activate`
    *   **macOS/Linux (bash):** `source venv/bin/activate`
    *(You should see `(venv)` appear at the beginning of your terminal prompt.)*
4.  **Install Packages:** Run the following command to install the necessary libraries (`tqdm`, `azure-ai-vision-imageanalysis`, and `python-dotenv`).
    ```bash
    pip install -r requirements.txt
    ```

---

### Part 4: Find the Caption Separator Value

The `CAPTION_SEPARATOR_Y_PIXEL` is the most important setting. It defines a horizontal line on your images. Any text *above* this line is considered slide content, and any text *below* it is considered a caption.

**How to Find the Right Value:**

1.  Navigate to your screenshots folder and open a typical screenshot in an image editor like **MS Paint**, **GIMP**, or **Photoshop**.
2.  Move your mouse cursor to the space **between** the main slide content and the caption text.
3.  Look at the status bar (usually at the bottom) of the image editor. It will show you the X and Y coordinates of your cursor.
4.  Note the **Y-coordinate**. This is your `CAPTION_SEPARATOR_Y_PIXEL` value.
5.  Open your `.env` file and update the `CAPTION_SEPARATOR_Y_PIXEL` value with this number.

*For example, if your images are 1920x1080 and the captions always start below the 900-pixel mark, a value of `880` would be a safe choice.*

---

### Part 5: Run the Script

You are now ready to process your images! All configuration is done in the `.env` file.

1.  Make sure your virtual environment is still active (`(venv)` is visible in your terminal).
2.  Run the script from the project's root directory:
    ```bash
    python process_slides.py
    ```
3.  A progress bar will appear, showing the script analyzing each image. This may take some time depending on the number of images.
4.  Once complete, the script will print a summary, and you will find a new Markdown file (e.g., `course_notes.md`) in your project folder. This file contains your de-duplicated and organized notes.
