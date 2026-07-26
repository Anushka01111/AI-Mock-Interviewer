# app/api/session_routes.py

import os
import tempfile

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.session_schema import SessionCreate
from typing import List
from app.schemas.question_schema import QuestionCreate, QuestionResponse
from app.services.session_service import create_session
from app.services.question_service import create_question
from app.security.auth import get_current_user

from app.pipeline.resume_parser import parse_resume
from app.pipeline.question_generator import generate_questions
from app.pipeline.live_report_builder import build_live_feedback
from fastapi.responses import FileResponse
from app.pipeline.report_generator import build_pdf_report_from_data
from app.pipeline.live_report_builder import build_live_session_report
import os


router = APIRouter()


@router.get("/")
def home():
    return {"message": "Session API"}


@router.post("/")
def create_new_session(
    session: SessionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return create_session(db, session.candidate_name)


@router.post("/{session_id}/upload-resume", response_model=List[QuestionResponse])
def upload_resume(
    session_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF resumes are supported.")

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name

    try:
        resume_data = parse_resume(tmp_path)
        result = generate_questions(resume_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Question generation failed: {e}")
    finally:
        os.remove(tmp_path)

    saved_questions = []
    for q in result.get("questions", []):
        question = create_question(
            db,
            QuestionCreate(
                session_id=session_id,
                question_text=q["question"],
                ideal_answer=q.get("ideal_answer")
            )
        )
        saved_questions.append(question)

    return saved_questions

@router.get("/{session_id}/report")
def get_session_report(
    session_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    feedback = build_live_feedback(db, session_id)
    return feedback

@router.get("/{session_id}/report/pdf")
def get_session_report_pdf(
    session_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    feedback = build_live_feedback(db, session_id)

    if "error" in feedback:
        raise HTTPException(status_code=404, detail=feedback["error"])

    session_report = feedback.pop("session_report")

    os.makedirs("data/generated_reports", exist_ok=True)
    output_path = f"data/generated_reports/session_{session_id}_report.pdf"

    build_pdf_report_from_data(session_report, feedback, output_path)

    return FileResponse(
        output_path,
        media_type="application/pdf",
        filename=f"interview_report_session_{session_id}.pdf"
    )