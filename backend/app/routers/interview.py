from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, auth
from app.services import openai_service, pdf_service

router = APIRouter(prefix="/api/interview", tags=["interview"])


@router.post("/start", response_model=schemas.StartInterviewResponse)
def start_interview(
    payload: schemas.StartInterviewRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    resume_text = ""
    if payload.resume_id:
        resume = db.query(models.Resume).filter(
            models.Resume.id == payload.resume_id, models.Resume.user_id == current_user.id
        ).first()
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        resume_text = resume.parsed_text or ""

    session = models.InterviewSession(
        user_id=current_user.id,
        resume_id=payload.resume_id,
        target_role=payload.target_role,
        status="in_progress",
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    generated = openai_service.generate_questions(resume_text, payload.target_role, payload.num_questions)

    questions = []
    for i, q in enumerate(generated):
        question = models.InterviewQuestion(
            session_id=session.id,
            order_index=i,
            question_text=q["question_text"],
            category=q.get("category", "technical"),
        )
        db.add(question)
        questions.append(question)
    db.commit()
    for q in questions:
        db.refresh(q)

    return {"session_id": session.id, "questions": questions}


@router.post("/answer", response_model=schemas.SubmitAnswerResponse)
def submit_answer(
    payload: schemas.SubmitAnswerRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    question = db.query(models.InterviewQuestion).join(models.InterviewSession).filter(
        models.InterviewQuestion.id == payload.question_id,
        models.InterviewSession.user_id == current_user.id,
    ).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    session = db.query(models.InterviewSession).filter(models.InterviewSession.id == question.session_id).first()

    result = openai_service.evaluate_answer(
        question.question_text, payload.answer_text, question.category, session.target_role
    )

    question.answer_text = payload.answer_text
    question.technical_score = result["technical_score"]
    question.communication_score = result["communication_score"]
    question.feedback = result["feedback"]
    db.commit()

    return {
        "question_id": question.id,
        "technical_score": question.technical_score,
        "communication_score": question.communication_score,
        "feedback": question.feedback,
    }


@router.post("/{session_id}/complete", response_model=schemas.SessionSummary)
def complete_interview(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    session = db.query(models.InterviewSession).filter(
        models.InterviewSession.id == session_id, models.InterviewSession.user_id == current_user.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    questions = db.query(models.InterviewQuestion).filter(
        models.InterviewQuestion.session_id == session.id
    ).order_by(models.InterviewQuestion.order_index).all()

    answered = [q for q in questions if q.technical_score is not None]
    if not answered:
        raise HTTPException(status_code=400, detail="No answers submitted yet")

    session.overall_technical_score = sum(q.technical_score for q in answered) / len(answered)
    session.overall_communication_score = sum(q.communication_score for q in answered) / len(answered)
    session.status = "completed"

    report_path = pdf_service.generate_report(
        session, questions, current_user.full_name or current_user.email, session.target_role
    )
    session.report_path = report_path
    db.commit()
    db.refresh(session)

    return {
        "session_id": session.id,
        "status": session.status,
        "overall_technical_score": session.overall_technical_score,
        "overall_communication_score": session.overall_communication_score,
        "report_path": session.report_path,
    }


@router.get("/{session_id}/report")
def download_report(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    session = db.query(models.InterviewSession).filter(
        models.InterviewSession.id == session_id, models.InterviewSession.user_id == current_user.id
    ).first()
    if not session or not session.report_path:
        raise HTTPException(status_code=404, detail="Report not found")

    return FileResponse(session.report_path, media_type="application/pdf", filename="interview_feedback_report.pdf")
