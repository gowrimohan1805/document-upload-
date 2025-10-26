from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import uuid
import os
from pathlib import Path
from typing import List
from pydantic import BaseModel

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./optiextract.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database model
class FileMetadata(Base):
    __tablename__ = "file_metadata"
    
    id = Column(Integer, primary_key=True, index=True)
    original_filename = Column(String, nullable=False)
    system_filename = Column(String, unique=True, nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models for API responses
class FileMetadataResponse(BaseModel):
    id: int
    original_filename: str
    system_filename: str
    file_size_bytes: int
    uploaded_at: datetime
    
    class Config:
        from_attributes = True

class UploadResponse(BaseModel):
    message: str
    original_filename: str
    system_filename: str
    file_size_bytes: int
    uploaded_at: datetime

# Create upload directory
UPLOAD_DIR = Path("./uploaded_files")
UPLOAD_DIR.mkdir(exist_ok=True)

# FastAPI app
app = FastAPI(title="OptiExtract Document Ingestion API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/upload-document", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document file and store its metadata in the database.
    """
    try:
        # Generate unique system filename
        file_extension = Path(file.filename).suffix
        system_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = UPLOAD_DIR / system_filename
        
        # Read and save file
        contents = await file.read()
        file_size = len(contents)
        
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Store metadata in database
        db = next(get_db())
        db_file = FileMetadata(
            original_filename=file.filename,
            system_filename=system_filename,
            file_size_bytes=file_size,
            uploaded_at=datetime.utcnow()
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        
        return UploadResponse(
            message="File uploaded successfully",
            original_filename=db_file.original_filename,
            system_filename=db_file.system_filename,
            file_size_bytes=db_file.file_size_bytes,
            uploaded_at=db_file.uploaded_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/files", response_model=List[FileMetadataResponse])
async def get_files():
    """
    Retrieve all uploaded file metadata from the database.
    """
    try:
        db = next(get_db())
        files = db.query(FileMetadata).order_by(FileMetadata.uploaded_at.desc()).all()
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve files: {str(e)}")

# Serve static HTML files
@app.get("/")
async def serve_upload_page():
    return FileResponse("pages/upload.html")

@app.get("/history")
async def serve_history_page():
    return FileResponse("pages/history.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)