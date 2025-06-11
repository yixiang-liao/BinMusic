import requests
import base64
import os
from dotenv import load_dotenv
from datetime import datetime
from db.session import SessionLocal
from db.model.artists import Artist
import json

# 載入 .env 檔案中的 client_id / client_secret
load_dotenv()
client_id = os.getenv("SPOTIFY_ID")
client_secret = os.getenv("SPOTIFY_SECRET")

base_url = "https://api.spotify.com/v1"

# 取得 Access Token
def get_access_token_Spotify():
    auth_str = f"{client_id}:{client_secret}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()

    response = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={
            "Authorization": f"Basic {b64_auth_str}",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={"grant_type": "client_credentials"}
    )

    if response.status_code != 200:
        raise Exception(f"取得 token 失敗: {response.text}")

    return response.json()["access_token"]

def get_artist_Spotify(artist_id, token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept-Language": "zh-TW"
    }

    params = {
        "include_groups": "album,single",  # 只要專輯與單曲
        "market": "TW",                    # 台灣地區可聽的作品
        "limit": 50,                       # 回傳最多幾筆
        "offset": 0                        # 從第幾筆開始
    }

    url = f"{base_url}/artists/{artist_id}"
    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        raise Exception(f"查詢失敗: {response.text}")
    
    artist = response.json()
    # print(artist)
    return {
        # "name": artist["name"],
        "genres": artist["genres"],
        "followers": artist["followers"]['total'],
        "popularity": artist["popularity"]
    }

# 查詢藝人專輯
def get_artist_albums_Spotify(artist_id, token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept-Language": "zh-TW"
    }

    params = {
        "include_groups": "album,single",  # 只要專輯與單曲
        "market": "TW",                    # 台灣地區可聽的作品
        "limit": 50,                       # 回傳最多幾筆
        "offset": 0                        # 從第幾筆開始
    }


    url = f"{base_url}/artists/{artist_id}/albums"
    response = requests.get(url, headers=headers , params=params)

    if response.status_code != 200:
        raise Exception(f"查詢專輯失敗: {response.text}")

    albums_data ={}

    albums = response.json()["items"]
    # print(albums)

    for album in albums:
        if album["album_type"] == "single" and album["total_tracks"] > 1:
            type = "EP"
        else:
            type = album["album_type"]
        albums_data[album["id"]] = {
            "name": album["name"],
            "album_type": type,
            "release_date": datetime.strptime(album["release_date"], "%Y-%m-%d").date(),
            "total_tracks": album["total_tracks"],
            "id": album["id"]
        }

    sorted_albums = dict(sorted(
        albums_data.items(),
        key=lambda item: item[1]["release_date"],
        reverse=True
    ))

    return sorted_albums

    # for album_id, info in sorted_albums.items():
    #     print(f"{info['release_date']} \t {info['name']} ({info['album_type']}) \t total_tracks: {info['total_tracks']} \t id: {info['id']}")
    # print("-"*5)

# 查詢藝人專輯封面
def get_artist_albums_cover_Spotify(artist_id, token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept-Language": "zh-TW"
    }

    params = {
        "include_groups": "album,single",  # 只要專輯與單曲
        "market": "TW",                    # 台灣地區可聽的作品
        "limit": 50,                       # 回傳最多幾筆
        "offset": 0                        # 從第幾筆開始
    }


    url = f"{base_url}/artists/{artist_id}/albums"
    response = requests.get(url, headers=headers , params=params)

    if response.status_code != 200:
        raise Exception(f"查詢專輯失敗: {response.text}")

    albums_data ={}

    albums = response.json()["items"]
    # print(albums)

    for album in albums:
        if album["album_type"] == "single" and album["total_tracks"] > 1:
            type = "EP"
        else:
            type = album["album_type"]
        albums_data[album["id"]] = {
            "name": album["name"],
            "images": album["images"],
            # "album_type": type,
            "release_date": datetime.strptime(album["release_date"], "%Y-%m-%d").date(),
            # "total_tracks": album["total_tracks"],
            "id": album["id"]
        }

    sorted_albums = dict(sorted(
        albums_data.items(),
        key=lambda item: item[1]["release_date"],
        reverse=True
    ))

    return sorted_albums

def safe_json_str(lst):
    """非空 list 則轉為 JSON 字串，否則回傳 None"""
    return json.dumps(lst, ensure_ascii=False) if lst else None

# 主程式
if __name__ == "__main__":
    db = SessionLocal()
    artist_list = db.query(Artist).all()
    token = get_access_token_Spotify()

    count = 1

    for user in artist_list:
        print(f"{count} - {user.name}")
        spotify_ids = json.loads(user.spotify_id) if user.spotify_id else []
        genres = []

        for sid in spotify_ids:
            artist_data = get_artist_Spotify(sid, token)
            print(f"粉絲數：{artist_data['followers']}")
            print(f"popularity：{artist_data['popularity']}")
            for genre in artist_data.get("genres", []):
                if genre not in genres:
                    genres.append(genre)
            get_artist_albums_Spotify(sid, token)

        genre_json = safe_json_str(genres)
        print(f"類型：{genres}")


        print("=====================================")
        count += 1

    db.close()