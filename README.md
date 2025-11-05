# Slide Text Extractor

This project uses Azure AI Vision to process a large number of course screenshots, de-duplicate them based on their visual text content, and merge all unique captions into a single, ordered Markdown document.

---

## 📚 Full Setup Guide

For detailed, step-by-step instructions on setting up and running this project, please see:

➡️ **[Complete User Guide (GUIDE.md)](GUIDE.md)**

## 🚀 Quick Start (Windows)

1. **First-time setup:**
   - Double-click `SETUP.bat` to install everything automatically
   - Configure your `.env` file (rename `.env.example` to `.env` and add your settings)

2. **Run the script:**
   - Double-click `RUN.bat` to process your images

The guide covers:
- Creating your Azure AI resource
- Configuring all settings in the `.env` file (credentials, paths, and options)
- Installing dependencies
- Finding the correct caption separator value
- Running the script

## ⚙️ Configuration

All configuration is managed through the `.env` file. Simply rename `.env.example` to `.env` and update:
- **AZURE_ENDPOINT**: Your Azure endpoint URL
- **AZURE_KEY**: Your Azure key
- **IMAGE_FOLDER_PATH**: Path to your screenshots folder
- **OUTPUT_FILE**: Name of the output file
- **CAPTION_SEPARATOR_Y_PIXEL**: Y-pixel value to separate slides from captions

The script will process all images and generate the specified output file in the project directory.
