# Future Development Roadmap

This document outlines the planned features and improvements for the Slide Text Extractor project.

---

## Phase 1: Enhanced Output Formatting ✅ COMPLETED

**Goal:** Preserve the original slide structure with proper line breaks, bullet points, and paragraphs.

**Problem Solved:** Previously, all text was joined into one continuous line, losing important formatting structure.

**Implementation Details:**
- Added intelligent text formatting function (`_format_text_with_structure()`)
- Detects and preserves bullet points (•, *, -, ▪, ►, →)
- Detects and preserves numbered lists (1., 2., 3., etc.)
- Detects and preserves lettered lists (a., b., c., etc.)
- Identifies headings (ALL CAPS or Title Case)
- Intelligently joins continuing paragraph text
- Uses regex patterns to recognize list markers
- Preserves line breaks in final Markdown output

**Testing:** Comprehensive test suite created (`test_formatting.py`) validates:
- Bullet point preservation
- Numbered list preservation
- Mixed content handling
- Paragraph continuation logic

**Impact:** Output notes now maintain the original slide structure, making them significantly more readable and useful.



---

## Phase 2: Logging and Metadata ✅ COMPLETED

**Goal:** Add professional logging and detailed processing information.

**Implementation Details:**
- **Logging System:** Implemented Python's built-in `logging` module
  - Logs written to `processing.log` with timestamps
  - Dual output: both file and console
  - Different log levels (INFO, WARNING, ERROR, DEBUG)
  
- **Processing Statistics:**
  - Total file count and size (human-readable format: MB, GB)
  - Files processed vs skipped vs failed
  - Total processing time and average time per image
  - Detailed start/end timestamps

- **Smart Duplicate Detection:**
  - Cache system (`.processed_images.json`) tracks processed files
  - Compares file name, size, and modification time
  - Skips already-processed images (saves time and API costs)
  - Automatic cache persistence across runs

- **Date-Based Sorting:**
  - Images sorted by creation date (oldest first)
  - Maintains original lecture/recording order
  - Ensures notes follow chronological sequence

- **Enhanced Output:**
  - Notes file includes generation timestamp
  - Total slide count in header
  - Better success/error messages

**Testing:** Verified with multiple runs:
- First run: Processed 2 images in 11.23 seconds
- Second run: Skipped 2 images in 0.02 seconds (99.8% faster!)

**Impact:** 
- Professional-grade logging for debugging
- Significant time savings on re-runs
- Chronological ordering ensures accurate note sequence
- Detailed metrics for tracking performance

---

## Phase 3: Simple Web Interface 🌐

**Goal:** Create an easy-to-use web interface for non-technical users.

**Framework:** Streamlit (Python-based, rapid development)

**Features:**
- Drag-and-drop file uploader for screenshots
- Interactive slider to adjust the caption separator value
- Live preview of processing progress
- Download button for the generated course notes
- Settings panel for output customization

**Difficulty:** Medium-Hard (8/10)

**Status:** Planned

---

## Phase 4: Image and Chart Extraction 📷 (Advanced)

**Goal:** Extract and save images, charts, and diagrams from slides as separate files.

**Approach:**
- Integrate Azure AI Document Intelligence (Layout model)
- Use the Layout API to detect image regions and figures
- Crop and save detected images using the Pillow library
- Embed image references in the Markdown output (e.g., `![Chart 1](slide_5_chart_1.png)`)

**Difficulty:** Hard (9/10)

**Status:** Future Consideration

---

## Phase 5: REST API Backend 🔌 (Professional Architecture)

**Goal:** Convert the core processing logic into a reusable REST API service.

**Framework:** FastAPI (Python, modern, high-performance)

**Architecture:**
- **Backend Repo (`slide-extractor-api`):** FastAPI service with endpoints for image upload, processing, and result retrieval
- **Frontend Repo (Separate):** Vue.js application that consumes the API

**API Endpoints (Planned):**
- `POST /api/extract` - Upload images and receive processed Markdown
- `GET /api/status/{job_id}` - Check processing status
- `GET /api/download/{job_id}` - Download completed notes

**Difficulty:** Very Hard (10/10)

**Status:** Long-term Goal

---

## Phase 6: Vue.js Frontend 🎨 (Modern UI)

**Goal:** Build a modern, responsive web application for the Slide Text Extractor.

**Framework:** Vue.js (JavaScript)

**Features:**
- Beautiful, modern user interface
- Multi-file upload with drag-and-drop
- Real-time processing progress updates
- Interactive preview of extracted slides
- Export options (Markdown, PDF, HTML)
- User authentication and project management (optional)

**Integration:** Connects to the FastAPI backend (Phase 5)

**Difficulty:** Medium-Hard (8/10)

**Status:** Long-term Goal

---

## Phase 7: PDF Document Support 📄 (Separate Project Recommended)

**Goal:** Extract and format text from PDF lecture notes and textbooks in a book-style continuous format.

**Key Differences from Image Slides:**
- **No caption separation** - PDFs have continuous text flow
- **Book-style output** - Chapters and sections, not individual slides
- **No de-duplication** - Each page contains unique content
- **Different structure** - Paragraphs, headings, tables vs. slide + caption

**Recommendation: CREATE SEPARATE PROJECT** ⭐

**Why Separate Repository:**
1. **Different Use Case:**
   - Slide Extractor: Video lecture screenshots with captions
   - PDF Extractor: Textbook/document continuous reading

2. **Different Output Format:**
   - Slides: Individual slides with merged captions
   - PDFs: Book chapters with continuous text flow

3. **Different Processing Logic:**
   - Slides: De-duplicate slides, merge captions, pixel-based separation
   - PDFs: Page ordering, chapter detection, paragraph flow

4. **Different Azure Service:**
   - Slides: Azure AI Vision (Computer Vision Read API)
   - PDFs: Azure AI Document Intelligence (Layout model)
     - Better for structured documents
     - Understands headings, paragraphs, tables
     - Handles multi-column layouts
     - Extracts reading order

5. **Cleaner Codebase:**
   - Each tool focused on one purpose
   - Easier to maintain and extend
   - Independent deployment schedules

**New Project: `PDF-Book-Extractor`**

**Features:**
- Extract text from PDF lecture notes/textbooks
- Detect and preserve chapter/section structure
- Maintain proper reading order and flow
- Handle tables and lists
- Book-style Markdown output
- Optional: Extract embedded images and diagrams

**Technology Options:**
- **Option A:** Azure AI Document Intelligence (best quality, paid)
- **Option B:** PyPDF2 + pdfplumber (free, offline, good quality)
- **Option C:** PyMuPDF (fast, comprehensive)

**Difficulty:** Medium (7/10)

**Status:** Future Separate Project

**Dependencies:** Can reuse logging/caching concepts from Phase 2

---

## Recommended Implementation Order

1. ✅ **Phase 2** (Logging) → COMPLETED
2. ✅ **Phase 1** (Formatting) → COMPLETED
3. **Phase 3** (Streamlit UI) → UI for image slide processing
4. **Phase 5** (FastAPI Backend) → API for slide extraction
5. **Phase 6** (Vue.js Frontend) → Modern UI for slide tool
6. **Phase 4** (Image Extraction) → Advanced feature for slides
7. **Phase 7** (PDF Support) → Separate project for book-style documents

---

## Notes

- ✅ Phases 1-2 are complete with robust foundation
- Phases 1-4 focus on perfecting the slide extraction tool
- **Phase 7 (PDF) should be a separate repository** due to different use case and output format
- Phases 5-6 can create API/UI for the slide extractor
- PDF Book Extractor can follow similar architecture patterns but remain independent
