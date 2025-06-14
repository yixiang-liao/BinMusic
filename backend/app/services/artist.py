from sqlalchemy.orm import Session
from collections import Counter
import json
from app.db.models.artists import Artist
from app.db.models.album import Album , Lyric, LyricLine
from datetime import datetime
import re

# 停用詞清單
STOPWORDS = set([
    "的", "了", "是", "在", "我", "你", "他", "她", "它", "我們", "也", "都",
    "和", "跟", "有", "沒", "不", "就", "很", "還", "但", "啊", "喔", "啦", "呢",
    "嗎", "吧", "而", "以", "被", "把", "與", "對", "像", "因為", "所以", "如果"
])

# 允許的詞性（名詞、動詞）
ALLOWED_POS = set(["N", "Na", "Nb", "Nc", "V", "VA", "VB", "VC"])

def clean_word(word: str) -> bool:
    if not word.strip():
        return False
    if re.fullmatch(r"\W+", word):  # 純標點
        return False
    if word in STOPWORDS:
        return False
    return True

def update_word_counter(word_counter: Counter, ws_result, pos_result):
    try:
        words = json.loads(ws_result)
        poses = json.loads(pos_result)
        for line_words, line_pos in zip(words, poses):
            for word, pos in zip(line_words, line_pos):
                if clean_word(word) and pos in ALLOWED_POS:
                    word_counter[word] += 1
    except Exception:
        pass

def get_artist_stats(artist_id: int, db: Session):
    total_albums = db.query(Album).filter(Album.artist_id == artist_id).count()
    total_lyrics = db.query(Lyric).filter(Lyric.artist_id == artist_id).count()
    total_lines = db.query(LyricLine).join(Lyric).filter(Lyric.artist_id == artist_id).count()

    lyrics = db.query(Lyric).filter(Lyric.artist_id == artist_id).all()
    topic_counter = Counter()
    word_counter = Counter()

    for lyric in lyrics:
        # 主題統計
        if hasattr(lyric, "predicted_topic") and lyric.predicted_topic:
            topic_counter[lyric.predicted_topic] += 1

        # 斷詞 + 詞性過濾詞頻
        if lyric.ws_result and lyric.pos_result:
            update_word_counter(word_counter, lyric.ws_result, lyric.pos_result)

    # 最終輸出前 30 個詞及出現次數
    top_words = [{"word": word, "count": count} for word, count in word_counter.most_common()]

    return {
        "artist_id": artist_id,
        "total_albums": total_albums,
        "total_lyrics": total_lyrics,
        "total_lyric_lines": total_lines,
        "topic_distribution": dict(topic_counter),
        "top_words": top_words
    }

def get_all_artists(db: Session):
    return db.query(Artist).all()


def get_album_count_by_year(artist_id: int, db: Session):
    albums = db.query(Album).filter(Album.artist_id == artist_id).all()
    year_counter = Counter()

    for album in albums:
        if album.release_date:
            try:
                year = datetime.strptime(album.release_date, "%Y-%m-%d").year
                year_counter[str(year)] += 1
            except:
                continue  # 格式錯誤略過

    return {
        "artist_id": artist_id,
        "year_counts": dict(sorted(year_counter.items()))
    }