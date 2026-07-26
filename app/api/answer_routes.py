import os
import tempfile

from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from app.security.auth import get_current_user
from app.pipeline.audio_converter import convert_to_wav

from app.database.connection import get_db
from app.schemas.answer_schema import (
    AnswerCreate,
    AnswerUpdate,
    AnswerResponse
)
from app.schemas.score_schema import ScoreCreate
from app.services.answer_service import (
    create_answer,
    get_all_answers,
    get_answer_by_id,
    update_answer,
    delete_answer
)
from app.services.question_service import get_question_by_id
from app.services.score_service import create_score
from app.pipeline.answer_scorer import score_answer
from app.pipeline.audio_pipeline import run_pipeline as run_audio_pipeline
from app.pipeline.facial_video_analyzer import get_facial_score

router = APIRouter()


# ─────────────────────────────────────────────────────────────
# Original text-only endpoint — kept for backward compatibility
# and quick testing without needing audio/video files.
# ─────────────────────────────────────────────────────────────

@router.post("/", response_model=AnswerResponse)
def add_answer(
    answer: AnswerCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    saved_answer = create_answer(db, answer)

    question = get_question_by_id(db, answer.question_id)

    if question and question.ideal_answer:
        result = score_answer(
            question=question.question_text,
            candidate_answer=answer.transcript,
            ideal_answer=question.ideal_answer
        )

        create_score(
            db,
            ScoreCreate(
                answer_id=saved_answer.answer_id,
                accuracy_score=result["weighted_accuracy_score"],
                speech_score=0.0,
                facial_score=0.0
            )
        )

    return saved_answer


# ─────────────────────────────────────────────────────────────
# New endpoint — accepts real audio + video files, runs the full
# pipeline: transcription, prosody/confidence scoring, facial
# emotion/pose scoring, and SBERT answer accuracy scoring.
# ─────────────────────────────────────────────────────────────

@router.post("/submit-with-media", response_model=AnswerResponse)
def submit_answer_with_media(
    question_id: int = Form(...),
    audio_file: UploadFile = File(...),
    video_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    question = get_question_by_id(db, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    raw_audio_path = None
    audio_path = None
    video_path = None

    try:
        # Save the raw upload first, using whatever extension it came with
        original_suffix = os.path.splitext(audio_file.filename)[1] or ".m4a"
        with tempfile.NamedTemporaryFile(suffix=original_suffix, delete=False) as tmp_raw_audio:
            tmp_raw_audio.write(audio_file.file.read())
            raw_audio_path = tmp_raw_audio.name

        # Convert to a proper 16kHz mono WAV, which the speech pipeline expects
        audio_path = raw_audio_path.replace(original_suffix, "_converted.wav")
        convert_to_wav(raw_audio_path, audio_path)

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp_video:
            tmp_video.write(video_file.file.read())
            video_path = tmp_video.name

        # ── Speech pipeline (Member 3) ──────────────────────────
        # WAV -> transcript + prosody + confidence score
        audio_result = run_audio_pipeline(audio_path, model_size="base", use_local=True)
        transcript_text = audio_result["transcript"]["text"]
        speech_confidence = audio_result["confidence"]["score_0_1"]

        # ── Facial pipeline (Member 4) ──────────────────────────
        # Video -> sampled frames -> emotion + head pose -> score
        facial_score = get_facial_score(video_path, sample_fps=5.0)

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Media processing failed: {e}")
    finally:
        if raw_audio_path and os.path.exists(raw_audio_path):
            os.remove(raw_audio_path)
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
        if video_path and os.path.exists(video_path):
            os.remove(video_path)

    # ── Save the answer with the real transcript ────────────────
    saved_answer = create_answer(
        db,
        AnswerCreate(question_id=question_id, transcript=transcript_text)
    )

    # ── Accuracy scoring (SBERT + keywords, Member 2) ───────────
    accuracy_score = 0.0
    if question.ideal_answer:
        result = score_answer(
            question=question.question_text,
            candidate_answer=transcript_text,
            ideal_answer=question.ideal_answer
        )
        accuracy_score = result["weighted_accuracy_score"]

    # ── Save the combined score row — all 3 real dimensions ────
    create_score(
        db,
        ScoreCreate(
            answer_id=saved_answer.answer_id,
            accuracy_score=accuracy_score,
            speech_score=speech_confidence,
            facial_score=facial_score
        )
    )

    return saved_answer


@router.get("/", response_model=List[AnswerResponse])
def get_answers(
    db: Session = Depends(get_db)
):
    return get_all_answers(db)

@router.get("/{answer_id}", response_model=AnswerResponse)
def get_answer(
    answer_id: int,
    db: Session = Depends(get_db)
):
    return get_answer_by_id(db, answer_id)

@router.put("/{answer_id}", response_model=AnswerResponse)
def edit_answer(
    answer_id: int,
    updated_answer: AnswerUpdate,
    db: Session = Depends(get_db)
):
    return update_answer(db, answer_id, updated_answer)

@router.delete("/{answer_id}", response_model=AnswerResponse)
def remove_answer(
    answer_id: int,
    db: Session = Depends(get_db)
):
    return delete_answer(db, answer_id)