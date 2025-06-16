from sqlalchemy.orm import Session
from app.db.models.album import LyricFeedback
from app.schemas.lyric_feedback import LyricFeedbackCreate
from app.db.models.album import LyricFeedback, LyricLine , Lyric
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

    # 撈對應歌詞行
    lines = db.query(LyricLine).filter(LyricLine.lyric_id == feedback.lyric_id).all()
    line_dict = {line.line_number: line.text for line in lines}

    # ✅ 組合 selected_lyrics
    selected_ids = feedback_data.selected_lines
    selected_lyrics = [line_dict.get(i, "") for i in selected_ids]

    return {
        "id": feedback.id,
        "lyric_id": feedback.lyric_id,
        "selected_lines": selected_ids,
        "selected_lyrics": selected_lyrics,
        "feeling": feedback_data.feeling,
        "reason": feedback_data.reason,
        "user_name": feedback_data.user_name
    }

def get_feedback_by_lyric(db: Session, lyric_id: int):
    feedbacks = db.query(LyricFeedback).filter(LyricFeedback.lyric_id == lyric_id).all()

    # 先撈出所有該歌詞的行號和內容
    all_lines = (
        db.query(LyricLine.line_number, LyricLine.text)
        .filter(LyricLine.lyric_id == lyric_id)
        .all()
    )
    line_dict = {line.line_number: line.text for line in all_lines}

    output = []
    for fb in feedbacks:
        selected_ids = json.loads(fb.selected_lines)
        feeling = json.loads(fb.feeling)

        selected_lyrics = [line_dict.get(i, "") for i in selected_ids]

        output.append({
            "id": fb.id,
            "lyric_id": fb.lyric_id,
            "selected_lines": selected_ids,
            "selected_lyrics": selected_lyrics,
            "feeling": feeling,
            "reason": fb.reason,
            "user_name": fb.user_name
        })
    
    return output

def get_lyrics_with_feedback(db: Session):
    results = (
        db.query(Lyric)
        .join(Lyric.feedbacks)
        .join(Lyric.album)
        .join(Lyric.artist)
        .filter(LyricFeedback.lyric_id == Lyric.id)
        .distinct()
        .all()
    )

    songs = []
    for lyric in results:
        songs.append({
            "lyric_id": lyric.id,
            "song_title": lyric.title,
            "artist_id": lyric.artist.id,  # 新增 artist_id 欄位
            "album_name": lyric.album.album_name,
            "artist_name": lyric.artist.name,
            "kkbox_cover": lyric.album.kkbox_cover or "",  # 直接回傳原始 JSON 字串或空字串
        })

    return songs