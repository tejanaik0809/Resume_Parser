import os
import uuid
import json
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from pydantic import ValidationError

from app.utils.logger import logger
from app.models import UploadResponse, ErrorResponse, ResumeData
from app.services.parser import extract_text_from_file
from app.services.llm_service import parse_with_llm

app = FastAPI(
    title="Resume Parser API",
    description="API to upload PDF/DOCX resumes and extract information using Local LLM.",
    version="1.0.0"
)

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "uploads")
PARSED_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "parsed")

Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
Path(PARSED_DIR).mkdir(parents=True, exist_ok=True)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up FastAPI application...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down FastAPI application...")

@app.post("/api/upload", response_model=UploadResponse, status_code=status.HTTP_200_OK, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def upload_resume(file: UploadFile = File(...)):
    # Handle file upload and parse via LLM
    if not file.filename:
        logger.warning("Upload attempt without filename.")
        raise HTTPException(status_code=400, detail="No file uploaded.")
        
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ['.pdf', '.doc', '.docx']:
        logger.warning(f"Invalid file type uploaded: {ext}")
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF and DOCX are allowed.")
    
    document_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{document_id}{ext}")
    
    try:

        logger.info(f"Saving file {file.filename} as {document_id}{ext}")
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
            

        raw_text = extract_text_from_file(file_path)
        

        parsed_data = parse_with_llm(raw_text)
        
        if not parsed_data:
            raise ValueError("Failed to obtain parsed data from the text.")
            
        # Cache the result for future retrieval
        parsed_file_path = os.path.join(PARSED_DIR, f"{document_id}.json")
        with open(parsed_file_path, "w", encoding='utf-8') as f:
            f.write(parsed_data.model_dump_json(indent=2))
            
        logger.info(f"Successfully processed document {document_id}")
        return UploadResponse(
            document_id=document_id,
            status="success",
            message="Resume parsed successfully.",
            data=parsed_data
        )
        
    except ValueError as ve:
        logger.error(f"Validation error during processing: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected processing error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during resume processing.")


@app.get("/api/resume/{document_id}", response_model=ResumeData, responses={404: {"model": ErrorResponse}})
async def get_resume(document_id: str):
    # Fetch cached parsed data
    parsed_file_path = os.path.join(PARSED_DIR, f"{document_id}.json")
    
    if not os.path.exists(parsed_file_path):
        logger.info(f"Document {document_id} not found.")
        raise HTTPException(status_code=404, detail="Document not found.")
        
    try:
        with open(parsed_file_path, "r", encoding='utf-8') as f:
            data = json.load(f)
        return ResumeData(**data)
    except Exception as e:
        logger.error(f"Error retrieving parsed data for {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving resume data.")
