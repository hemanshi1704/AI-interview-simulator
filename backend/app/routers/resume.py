import os
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, auth
from app.config import get_settings
from app.services.resume_parser import extract_text

router = APIRouter(prefix="/api/resume", tags=["resume"])
settings = get_settings()

ALLOWED_EXT = {".pdf", ".docx", ".txt"}


@router.post("/upload", response_model=schemas.ResumeOut)
def upload_resume(
    file: UploadFile = File(...),
    target_role: str = Form(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(status_code=400, detail="Only .pdf, .docx, or .txt files are allowed")

    os.makedirs(settings.upload_dir, exist_ok=True)
    stored_name = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(settings.upload_dir, stored_name)

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    parsed_text = extract_text(file_path)

    resume = models.Resume(
        user_id=current_user.id,
        filename=file.filename,
        file_path=file_path,
        parsed_text=parsed_text,
        target_role=target_role,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


@router.get("/", response_model=list[schemas.ResumeOut])
def list_resumes(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Resume).filter(models.Resume.user_id == current_user.id).all()
