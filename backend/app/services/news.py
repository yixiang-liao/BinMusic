from sqlalchemy.orm import Session
from app.db.models.news import News
from collections import Counter, defaultdict
import json
from datetime import datetime
import re
from typing import List
from sqlalchemy import or_
import ast

def get_filtered_news(db: Session, start=None, end=None, tag=None, keyword=None):
    q = db.query(News)
    if start:
        q = q.filter(News.date >= start)
    if end:
        q = q.filter(News.date <= end)
    if tag:
        q = q.filter(News.tag.contains(tag))
    if keyword:
        q = q.filter(
            or_(
                News.title.contains(keyword),
                News.content.contains(keyword)
            )
        )
    return q.order_by(News.id.desc()).all()

def get_news_daily_counts(db: Session, start=None, end=None, tag=None, keyword=None):
    q = db.query(News)

    if start:
        q = q.filter(News.date >= start)
    if end:
        q = q.filter(News.date <= end)
    if tag:
        q = q.filter(News.tag.contains(tag))
    if keyword:
        q = q.filter(
            or_(
                News.title.contains(keyword),
                News.content.contains(keyword)
            )
        )

    all_news = q.all()

    count_by_month = defaultdict(int)
    for item in all_news:
        if isinstance(item.date, datetime):
            month_key = item.date.strftime('%Y-%m')  # 例：2024-06
        else:
            try:
                parsed_date = datetime.strptime(str(item.date), "%Y-%m-%d")
                month_key = parsed_date.strftime('%Y-%m')
            except:
                continue  # 若日期格式錯誤則略過

        count_by_month[month_key] += 1

    result = [{"date": d, "count": c} for d, c in sorted(count_by_month.items())]

    return { "counts": result }

def get_news_wordcloud(db: Session, start=None, end=None, tag=None, keyword=None):
    from ast import literal_eval
    import json

    q = db.query(News.id, News.title, News.ws_result)

    if start:
        q = q.filter(News.date >= start)
    if end:
        q = q.filter(News.date <= end)
    if tag:
        q = q.filter(News.tag.contains(tag))
    if keyword:
        q = q.filter(or_(
            News.title.contains(keyword),
            News.content.contains(keyword)
        ))

    news_list = q.order_by(News.date.desc()).limit(1000).all()
    print(f"🔍 符合條件的新聞數量: {len(news_list)}")

    all_words = []

    for news_id, title, result in news_list:
        try:
            if not result or result.lower() in ("null", "none", "nan", ""):
                continue

            try:
                ws_data = json.loads(result)
            except:
                ws_data = literal_eval(result)

            if isinstance(ws_data, list):
                if all(isinstance(w, str) for w in ws_data):
                    flat_words = [w.strip() for w in ws_data]
                else:
                    flat_words = [w.strip() for line in ws_data if isinstance(line, list) for w in line]
            else:
                flat_words = []

            all_words.extend(flat_words)

        except Exception as e:
            print(f"⚠️ 處理失敗 id={news_id}: {e}")
            continue

    # 過濾條件：字數 > 1 且不是純標點
    filtered_words = [w for w in all_words if len(w) > 1 and not re.fullmatch(r"[\s\W]+", w)]
    word_counter = Counter(filtered_words)

    print(f"✅ 完成詞頻統計，詞彙數={len(word_counter)}")
    return {"top_words": [{"word": w, "count": c} for w, c in word_counter.most_common(100)]}

def get_artist_volume(db: Session, artist_names: List[str]):
    # 統計藝人名字在 title 或 content 中的出現次數
    volume_data = {name: defaultdict(int) for name in artist_names}
    all_news = db.query(News).all()

    for news in all_news:
        for artist in artist_names:
            if artist in news.title or artist in (news.content or ""):
                month = news.date[:7] if news.date else "unknown"
                volume_data[artist][month] += 1

    result = [
        {
            "artist_name": artist,
            "data": dict(sorted(volume_data[artist].items()))
        }
        for artist in artist_names
    ]
    return result
