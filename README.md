# OptiExtract - Document Ingestion Platform

A complete web application for document upload, storage, and metadata management.

## Features
✅ File upload with drag-and-drop support
✅ Unique UUID-based file storage
✅ SQLite database for metadata persistence
✅ Upload history with statistics
✅ RESTful API with FastAPI

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Server
```bash
python main.py
```

### 3. Open Browser
- Upload Page: http://localhost:8000/
- History Page: http://localhost:8000/history

## Project Structure

optiextract/
├── main.py                 # FastAPI backend
├── requirements.txt        # Python dependencies
├── pages/
│   ├── upload.html        # Upload interface
│   └── history.html       # History interface
├── uploaded_files/        # Stored files (auto-created)
└── optiextract.db         # SQLite database (auto-created)


## API Endpoints
- `POST /upload-document` - Upload a file
- `GET /files` - Get all file metadata
- `GET /` - Serve upload page
- `GET /history` - Serve history page

## Technologies
- Python 3.8+
- FastAPI
- SQLAlchemy
- SQLite
- HTML5/CSS3/JavaScript
