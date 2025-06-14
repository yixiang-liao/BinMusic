from sqlalchemy.orm import Session
from app.db.models.album import Album, Lyric
from collections import Counter
import json
import re
from sqlalchemy.orm import joinedload

# 停用詞與詞性設定
STOPWORDS = set(["的", "是", "了", "在", "就", "不", "和", "我", "你", "他", "她", "也", "都"])
ALLOWED_POS = set(["N", "Na", "Nb", "Nc", "V", "VA", "VB", "VC"])

# 過濾條件：非空、非標點、非停用詞
def clean_word(word: str) -> bool:
    return word and not re.fullmatch(r"\W+", word) and word not in STOPWORDS

# 專輯列表
def get_all_albums(db: Session):
    return (
        db.query(Album)
        .filter(Album.kkbox_id.isnot(None), Album.kkbox_id != "",
            db.query(Lyric.id).filter(Lyric.album_id == Album.id).exists())
        .options(joinedload(Album.artist))
        .all()
    )

# 每首歌情緒分析（預設 0.0）
def get_album_emotions(album_id: int, db: Session):
    lyrics = db.query(Lyric).filter(Lyric.album_id == album_id).all()
    return {
        "album_id": album_id,
        "emotions": [
            {"title": lyric.title, "emotion_score": lyric.emotion_score or 0.0, "emotion_label": lyric.emotion_label or "未知"}
            for lyric in lyrics
        ]
    }

# 專輯文字雲（斷詞 + 詞性過濾）
def get_album_top_words(album_id: int, db: Session):
    lyrics = db.query(Lyric).filter(Lyric.album_id == album_id).all()
    word_counter = Counter()

    for lyric in lyrics:
        try:
            words = json.loads(lyric.ws_result or "[]")
            poses = json.loads(lyric.pos_result or "[]")
            for line_words, line_pos in zip(words, poses):
                for word, pos in zip(line_words, line_pos):
                    if clean_word(word) and pos in ALLOWED_POS:
                        word_counter[word] += 1
        except Exception:
            continue

    return {
        "album_id": album_id,
        "top_words": [{"word": w, "count": c} for w, c in word_counter.most_common()]
    }
