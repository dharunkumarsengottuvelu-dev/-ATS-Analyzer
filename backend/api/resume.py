from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.models.resume import Resume
from backend.models.user import User
from backend.api.deps import get_current_user_optional
from backend.parser.extract import extract_text_from_file
from backend.parser.ner import parse_resume
from backend.schemas.resume import UploadResponse
import os
import uuid

import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/resume",
    tags=["Resume"]
)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "../../uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=UploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Uploads a resume (PDF/DOCX), extracts text, performs initial parsing, and stores in DB.
    """
    if not file.filename.lower().endswith(('.pdf', '.docx', '.txt')):
        logger.warning(f"Validation failed: Invalid file type uploaded - {file.filename}")
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, and TXT files are supported.")

    try:
        import time
        timestamp = int(time.time())
        file_id = str(uuid.uuid4())
        ext = os.path.splitext(file.filename)[1]
        file_path = os.path.join(UPLOAD_DIR, f"resume_{timestamp}_{file_id}{ext}")
        
        file_bytes = await file.read()
        logger.info(f"Uploading file: {file.filename} size: {len(file_bytes)} bytes")
        
        if len(file_bytes) > 20 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 20MB.")
            
        user_id = current_user.id if current_user else 1
            
        with open(file_path, "wb") as f:
            f.write(file_bytes)
            
        # Reset file pointer for extraction
        await file.seek(0)
        
        # 1. Extract text (with OCR fallback)
        raw_text = await extract_text_from_file(file)
        
        # 2. Parse text into structured data
        parsed_data = parse_resume(raw_text)
        
        # 3. Store in Database
        
        db_resume = Resume(
            user_id=user_id,
            filename=file.filename,
            file_path=file_path,
            file_type=ext.replace('.', ''),
            file_size_bytes=len(file_bytes),
            original_text=raw_text,
            parsed_data=parsed_data.model_dump()
        )
        db.add(db_resume)
        db.commit()
        db.refresh(db_resume)
        
        logger.info(f"Successfully processed and stored resume: {file.filename} (ID: {db_resume.id})")
        
        return UploadResponse(
            status="success",
            message="Resume parsed successfully.",
            filename=file.filename,
            parsed_data=parsed_data,
            resume_id=db_resume.id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_msg = str(e)
        logger.error(f"Error processing resume {file.filename}: {error_msg}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"An error occurred during parsing: {error_msg}")
