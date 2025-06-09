import requests
from bs4 import BeautifulSoup
import time
import os
import re

from sqlalchemy.orm import Session
from db.session import SessionLocal
from db.model.album import Album, LyricLine, Lyric
from db.model.artists import Artist
from ckip_transformers.nlp import CkipWordSegmenter, CkipPosTagger, CkipNerChunker
import json

# 初始化 CKIP 模型
ws_driver = CkipWordSegmenter(model="albert-tiny")
pos_driver = CkipPosTagger(model="albert-tiny")
ner_driver = CkipNerChunker(model="albert-tiny")

# === 清理 CKIP 結果 ===
def clean_ckip_lyrics(ws_result, pos_result, ner_result):
    cleaned_ws = []
    cleaned_pos = []
    cleaned_ner = []

    for i, tokens in enumerate(ws_result):
        # 濾掉純標點或空白的行（例如 ["，", "！"]）
        if all(re.match(r"^\W+$", token) for token in tokens):
            continue
        cleaned_ws.append(tokens)
        cleaned_pos.append(pos_result[i])
        cleaned_ner.append(ner_result[i])

    return cleaned_ws, cleaned_pos, cleaned_ner

# === 取得歌詞內容 ===
def get_lyrics(song_url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(song_url, headers=headers, timeout=10)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        lyrics_tag = soup.select_one("div.lyrics")
        if lyrics_tag:
            return lyrics_tag.get_text(separator="\n").strip()
    except Exception as e:
        print(f"❌ 無法擷取歌詞：{e}（{song_url}）")
    return None

# === 擷取專輯資訊並存入資料庫 ===
def crawl_and_save_to_db():
    db: Session = SessionLocal()
    albums = db.query(Album).filter(Album.kkbox_id.isnot(None)).all()
    print(f"📦 共 {len(albums)} 張專輯")

    for album in albums:
        kkbox_id = album.kkbox_id
        if not kkbox_id.strip():
            continue

        print(f"\n📀 專輯 KKBOX ID：{kkbox_id}")
        url = f"https://www.kkbox.com/tw/tc/album/{kkbox_id}"
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            res = requests.get(url, headers=headers, timeout=10)
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'html.parser')

            # 儲存專輯介紹
            desc_tag = soup.select_one("article.content-description")
            if desc_tag:
                album.description = desc_tag.get_text(separator="\n").strip()
                db.commit()

            ul = soup.select_one("div.content-tracks ul")
            if not ul:
                continue

            for li in ul.find_all("li"):
                song_tag = li.select_one(".song a")
                artist_tag = li.select_one(".artist")
                if song_tag and artist_tag:
                    title = song_tag.text.strip()
                    link = song_tag['href']
                    song_id = link.split('/')[-1]
                    # artist_name = artist_tag.text.strip()

                    # artist = db.query(Artist).filter_by(name=artist_name).first()
                    artist = db.query(Artist).filter_by(id=album.artist_id).first()
                    if not artist:
                        print(f"⚠️ 找不到藝人：{album.artist_id}")
                        continue

                    print(f"🎵 擷取歌曲：{title}")
                    lyrics = get_lyrics(link)
                    time.sleep(1)

                    if lyrics:
                        lines = [line.strip() for line in lyrics.split('\n') if line.strip()]
                        ws = ws_driver(lines)
                        pos = pos_driver(ws)
                        ner = ner_driver(ws)
                        ws_clean, pos_clean, ner_clean = clean_ckip_lyrics(ws, pos, ner)
                    else:
                        lines, ws_clean, pos_clean, ner_clean = [], [], [], []

                    # 儲存 Lyric
                    lyric = Lyric(
                        song_id=song_id,
                        title=title,
                        lyrics=lyrics,
                        artist_id=artist.id,
                        album_id=album.id,
                        ws_result=json.dumps(ws_clean, ensure_ascii=False),
                        pos_result=json.dumps(pos_clean, ensure_ascii=False),
                        ner_result=json.dumps(ner_clean, ensure_ascii=False),
                    )
                    db.add(lyric)
                    db.commit()

                    # 儲存每一行歌詞
                    for i, line in enumerate(lines, start=1):
                        db.add(LyricLine(
                            lyric_id=lyric.id,
                            line_number=i,
                            text=line
                        ))
                    db.commit()
        except Exception as e:
            print(f"❌ 錯誤：{e}（{kkbox_id}）")

    db.close()
    print("\n✅ 全部完成，已存入資料庫")

if __name__ == "__main__":
    crawl_and_save_to_db()
