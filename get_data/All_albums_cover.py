# import requests
# import os
# import json
# from dotenv import load_dotenv
# from db.session import SessionLocal
# from db.model.artists import Artist
# from db.model.album import Album , Lyric , LyricLine
# from get_kkbox import get_access_token_KKBOX
# from get_spotify import get_access_token_Spotify, get_artist_albums_cover_Spotify

# # 新增：透過專輯 ID 抓取 KKBOX 封面
# def get_album_cover_KKBOX(album_id: str, token: str):
#     headers = {
#         "accept": "application/json",
#         "authorization": f"Bearer {token}"
#     }
#     url = f"https://api.kkbox.com/v1.1/albums/{album_id}?territory=TW"
#     response = requests.get(url, headers=headers)
#     if response.status_code != 200:
#         raise Exception(f"查詢失敗: {response.text}")
#     return response.json().get("images", [])

# # 初始化
# load_dotenv()
# db = SessionLocal()
# token_KKBOX = os.getenv("KKBOX_TOKEN") or get_access_token_KKBOX()
# token_Spotify = get_access_token_Spotify()

# # 建立對照表
# kkbox_cover_map = {}
# spotify_cover_map = {}

# # 先抓 KKBOX Cover
# kkbox_ids = [row[0] for row in db.query(Album.kkbox_id).filter(Album.kkbox_id.isnot(None)).distinct().all()]
# for kid in kkbox_ids:
#     try:
#         images = get_album_cover_KKBOX(kid, token_KKBOX)
#         if images:
#             kkbox_cover_map[kid] = images
#     except Exception as e:
#         print(f"KKBOX 錯誤（{kid}）：{e}")

# # 再抓 Spotify Cover
# spotify_ids = [row[0] for row in db.query(Album.spotify_id).filter(Album.spotify_id.isnot(None)).distinct().all()]
# for sid in spotify_ids:
#     try:
#         albums = get_artist_albums_cover_Spotify(sid, token_Spotify)
#         for album_id, info in albums.items():
#             spotify_cover_map[album_id] = info.get("images", [])
#     except Exception as e:
#         print(f"Spotify 錯誤（{sid}）：{e}")

# # 寫入 albums 資料表
# albums = db.query(Album).all()
# for album in albums:
#     updated = False

#     if album.kkbox_id in kkbox_cover_map:
#         album.kkbox_cover = json.dumps(kkbox_cover_map[album.kkbox_id], ensure_ascii=False)
#         updated = True

#     if album.spotify_id in spotify_cover_map:
#         album.spotify_cover = json.dumps(spotify_cover_map[album.spotify_id], ensure_ascii=False)
#         updated = True

#     if updated:
#         print(f"✅ 更新 Album：{album.album_name or album.id}")

# # 儲存到資料庫
# db.commit()
# db.close()

import requests
import os
import json
from dotenv import load_dotenv
from db.session import SessionLocal
from db.model.album import Album
from get_spotify import get_access_token_Spotify

# ✅ 新增：用專輯 ID 抓封面
def get_album_cover_Spotify(album_id: str, token: str):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    url = f"https://api.spotify.com/v1/albums/{album_id}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Spotify 查詢失敗（{album_id}）: {response.text}")
    return response.json().get("images", [])

# 初始化
load_dotenv()
db = SessionLocal()
token_Spotify = get_access_token_Spotify()

# 建立封面對照表
spotify_cover_map = {}

# 抓所有 spotify 專輯 ID
spotify_ids = [row[0] for row in db.query(Album.spotify_id).filter(Album.spotify_id.isnot(None)).distinct().all()]
for sid in spotify_ids:
    try:
        images = get_album_cover_Spotify(sid, token_Spotify)
        if images:
            spotify_cover_map[sid] = images
    except Exception as e:
        print(f"⚠️ Spotify 錯誤（{sid}）：{e}")

# 更新資料表
albums = db.query(Album).all()
for album in albums:
    if album.spotify_id in spotify_cover_map:
        album.spotify_cover = json.dumps(spotify_cover_map[album.spotify_id], ensure_ascii=False)
        print(f"✅ 已更新 Spotify 專輯：{album.album_name or album.id}")

# 寫入 DB
db.commit()
db.close()
