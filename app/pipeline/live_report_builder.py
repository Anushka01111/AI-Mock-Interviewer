"""
live_report_builder.py
-----------------------
Bridges live database data (Question, Answer, Score) into the format
expected by session_aggregator.py, feedback_synthesizer.py, and
report_generator.py — which were originally built to read local JSON files.
"""

from sqlalchemy.orm import Session as DBSession
from app.models.question import Question
from app.models.answer import Answer
from app.models.score import Score

from app.pipeline.session_aggregator import (
    merge_session_scores,
    compute_dimension_stats,
    calibrate_thresholds
)
from app.pipeline.feedback_synthesizer import generate_feedback


def get_session_scores(db: DBSession, session_id: int) -> dict:
    """
    Query all questions for a session, join their answers and scores,
    and reshape into the accuracy/speech/facial record format that
    session_aggregator.py expects (list of dicts keyed by 'id').
    """
    questions = db.query(Question).filter(Question.session_id == session_id).all()

    accuracy_records = []
    speech_records = []
    facial_records = []

    for q in questions:
        answer = db.query(Answer).filter(Answer.question_id == q.question_id).first()
        if not answer:
            continue

        score = db.query(Score).filter(Score.answer_id == answer.answer_id).first()
        if not score:
            continue

        accuracy_records.append({
            "id": q.question_id,
            "weighted_accuracy_score": score.accuracy_score
        })
        speech_records.append({
            "id": q.question_id,
            "confidence_score": score.speech_score,
            "clarity": score.speech_score  # placeholder until Member 3 splits these
        })
        facial_records.append({
            "id": q.question_id,
            "emotion_score": score.facial_score,
            "eye_contact_ratio": score.facial_score  # placeholder until Member 4 splits these
        })

    return {
        "accuracy": accuracy_records,
        "speech": speech_records,
        "facial": facial_records
    }


def build_live_session_report(db: DBSession, session_id: int, threshold: float = 0.5) -> dict:
    """
    Full pipeline: query DB -> merge into DataFrame -> compute stats ->
    flag thresholds -> return session report dict (same shape session_aggregator
    produces from JSON files).
    """
    records = get_session_scores(db, session_id)

    if not records["accuracy"]:
        return {"session_summary": {}, "per_question": []}

    merged_df = merge_session_scores(
        records["accuracy"],
        records["speech"],
        records["facial"]
    )

    numeric_columns = [
        "accuracy_weighted_accuracy_score",
        "speech_confidence_score",
        "speech_clarity",
        "facial_emotion_score",
        "facial_eye_contact_ratio"
    ]

    dimension_stats = compute_dimension_stats(merged_df, numeric_columns)
    flagged_df = calibrate_thresholds(merged_df, numeric_columns, threshold)

    return {
        "session_summary": dimension_stats,
        "per_question": flagged_df.to_dict(orient="records")
    }


def build_live_feedback(db: DBSession, session_id: int) -> dict:
    """
    Full flow: build the session report from live DB data, then
    generate narrative feedback via the LLM.
    """
    session_report = build_live_session_report(db, session_id)

    if not session_report["per_question"]:
        return {
            "error": "No scored answers found for this session yet."
        }

    feedback = generate_feedback(session_report)
    feedback["session_report"] = session_report

    return feedback