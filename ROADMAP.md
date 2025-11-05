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

**Difficulty:** Medium (6/10)

**Status:** ✅ Completed

---

## Phase 2: Logging and Metadata 📊 (Quick Win)

**Goal:** Add professional logging and detailed processing information.

**Features:**
- Display total file count and size before processing
- Write processing logs to a `processing.log` file with timestamps
- Track processing time per image and total duration
- Log warnings and errors for easier debugging

**Difficulty:** Easy (4/10)

**Status:** Planned

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

## Recommended Implementation Order

1. **Phase 2** (Logging) → Easiest, helps with debugging all future features
2. **Phase 1** (Formatting) → Makes output immediately more useful
3. **Phase 3** (Streamlit UI) → Quick way to make tool user-friendly
4. **Phase 5** (FastAPI Backend) → Foundation for professional architecture
5. **Phase 6** (Vue.js Frontend) → Modern UI for end users
6. **Phase 4** (Image Extraction) → Advanced feature, requires most research

---

## Notes

- Each phase builds on the previous one
- Phases 1-3 can be completed within the current Python project
- Phases 5-6 require creating new, separate repositories
- The API-based architecture (Phases 5-6) follows modern microservices best practices
