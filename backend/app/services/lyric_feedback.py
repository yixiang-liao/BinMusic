from sqlalchemy.orm import Session
from app.db.models.album import LyricFeedback
from app.schemas.lyric_feedback import LyricFeedbackCreate
import json

def create_feedback(db: Session, feedback_data: LyricFeedbackCreate):
    feedback = LyricFeedback(
        lyric_id=feedback_data.lyric_id,
        selected_lines=json.dumps(feedback_data.selected_lines, ensure_ascii=False),
        feeling=json.dumps(feedback_data.feeling, ensure_ascii=False),
        reason=feedback_data.reason,
        user_name=feedback_data.user_name
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback

def get_feedback_by_lyric(db: Session, lyric_id: int):
    return db.query(LyricFeedback).filter(LyricFeedback.lyric_id == lyric_id).all()