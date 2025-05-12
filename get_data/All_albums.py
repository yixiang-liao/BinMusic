import requests
import base64
import os
from dotenv import load_dotenv
from datetime import datetime, date
from db.session import SessionLocal
from db.model.artists import Artist
import json
import pandas as pd
from get_kkbox import get_access_token_KKBOX, get_artist_KKBOX, get_artist_albums_KKBOX
from get_spotify import get_access_token_Spotify, get_artist_Spotify, get_artist_albums_Spotify, safe_json_str
from difflib import get_close_matches

merged_results = []  # 用來儲存所有藝人合併結果

def merge_albums_by_name_and_date(artist_id,artist_name, spotify_album: dict, kkbox_album: dict, fuzzy_threshold: float = 0.7):
    spotify_album_dict = {}
    for album_id, info in spotify_album.items():
        name = info["name"].strip().lower()
        key = f"{info['release_date']}|{name}"
        spotify_album_dict[key] = {
            "name": info["name"],
            "release_date": info["release_date"],
            "album_type": info["album_type"],
            "total_tracks": info["total_tracks"],
            "spotify_id": info["id"]
        }

    # 整理 KKBOX 專輯資料
    kkbox_album_list = []
    for album_id, info in kkbox_album.items():
        kkbox_album_list.append({
            "date": info["release_date"],
            "name": info["name"].strip().lower(),
            "original_name": info["name"],
            "kkbox_id": album_id
        })

    matched_kkbox_ids = set()

    print("🎵 合併後專輯列表（以 Spotify 為主）：\n")
    for s_key, s_info in spotify_album_dict.items():
        s_date = s_info["release_date"]
        s_name = s_info["name"].strip().lower()
        matched = None

        # Stage 1: exact match
        for k in kkbox_album_list:
            if k["date"] == s_date and k["name"] == s_name:
                matched = k
                break

        # Stage 2: fuzzy title with same date
        if not matched:
            same_date_candidates = [k for k in kkbox_album_list if k["date"] == s_date]
            matches = get_close_matches(s_name, [k["name"] for k in same_date_candidates], n=1, cutoff=fuzzy_threshold)
            if matches:
                for k in same_date_candidates:
                    if k["name"] == matches[0]:
                        matched = k
                        break

        # Stage 3: fuzzy title only
        if not matched:
            matches = get_close_matches(s_name, [k["name"] for k in kkbox_album_list], n=1, cutoff=fuzzy_threshold)
            if matches:
                for k in kkbox_album_list:
                    if k["name"] == matches[0]:
                        matched = k
                        break

        # 印出合併結果
        print(f"{s_info['release_date']} - {s_info['name']} ({s_info['album_type']})")
        print(f"  ➤ Spotify ID: {s_info['spotify_id']}")
        if matched:
            print(f"  ➤ KKBOX 對應 ID: {matched['kkbox_id']}")
            matched_kkbox_ids.add(matched['kkbox_id'])
        else:
            print("  ➤ ❌ KKBOX 無對應")
        print("-" * 50)

        # 儲存進結果清單
        merged_results.append({
            "artist_id": artist_id,
            "artist": artist_name,
            "album_name": s_info['name'],
            "release_date": s_info['release_date'],
            "album_type": s_info['album_type'],
            "total_tracks": s_info['total_tracks'],
            "spotify_id": s_info['spotify_id'],
            "kkbox_id": matched['kkbox_id'] if matched else None
        })

    # 額外列出 KKBOX 無對應
    for k in kkbox_album_list:
        if k["kkbox_id"] not in matched_kkbox_ids:
            merged_results.append({
                "artist_id": artist_id,
                "artist": artist_name,
                "album_name": k['original_name'],
                "release_date": k['date'],
                "album_type": "N/A",
                "total_tracks": "N/A",
                "spotify_id": None,
                "kkbox_id": k['kkbox_id']
            })

# 轉換所有 datetime / date 為字串
def convert_date_fields(data_list):
    for item in data_list:
        for k, v in item.items():
            if isinstance(v, (datetime, date)):
                item[k] = v.strftime("%Y-%m-%d")
    return data_list

# ====== Main Logic Starts ======
db = SessionLocal()
artist_list = db.query(Artist).all()
count = 1

token_KKBOX = get_access_token_KKBOX()
token_Spotify = get_access_token_Spotify()

for user in artist_list:
    print(f"\n{count} - {user.name}")
    kkbox_ids = json.loads(user.kkbox_id) if user.kkbox_id else []
    spotify_ids = json.loads(user.spotify_id) if user.spotify_id else []

    genres = []
    followers = 0
    popularity = []
    combined_spotify_album = {}

    for sid in spotify_ids:
        artist_data = get_artist_Spotify(sid, token_Spotify)
        followers += artist_data.get('followers', 0)
        popularity.append(artist_data.get('popularity', 0))
        for genre in artist_data.get("genres", []):
            if genre not in genres:
                genres.append(genre)
        album_data = get_artist_albums_Spotify(sid, token_Spotify)
        for album_id, info in album_data.items():
            if info['name'] not in [a['name'] for a in combined_spotify_album.values()]:
                combined_spotify_album[album_id] = info

    if not kkbox_ids:
        print("⚠️ 無 KKBOX ID，跳過")
        count += 1
        continue

    kkbox_album = get_artist_albums_KKBOX(kkbox_ids[0], token_KKBOX)

    merge_albums_by_name_and_date(user.id, user.name, combined_spotify_album, kkbox_album)

    print(f"\n粉絲數：{followers}")
    print(f"popularity：{round(sum(popularity) / len(popularity), 1) if popularity else 'N/A'}")
    print(f"類型：{genres}")
    print("=====================================")
    count += 1

db.close()

# 處理資料並轉換格式
json_ready_data = convert_date_fields(merged_results)

# 建 DataFrame 並排序
df = pd.DataFrame(json_ready_data)
# 將 release_date 轉成 datetime 排序用
df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
df.sort_values(by=['artist_id', 'album_name', 'release_date'], inplace=True)

# 將 release_date 轉回字串避免 JSON 出錯
df['release_date'] = df['release_date'].dt.strftime('%Y-%m-%d')

# ✅ 將整個 df 全轉為字串（處理 None / NaT / NaN 問題）
df = df.astype(str).fillna("")

# 匯出 CSV
df.to_csv("merged_albums.csv", index=False, encoding="utf-8-sig")

# 匯出 JSON（已全為字串，不會錯）
with open("merged_albums.json", "w", encoding="utf-8") as f:
    json.dump(df.to_dict(orient="records"), f, ensure_ascii=False, indent=2)
