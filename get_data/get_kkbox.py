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
client_id = os.getenv("KKBOX_ID")
client_secret = os.getenv("KKBOX_SECRET")

base_url = "https://api.kkbox.com/v1.1/"


def parse_release_date(date_str):
    """
    處理可能為 YYYY-00-00、YYYY-MM-00、YYYY-MM-DD 的 release_date 字串
    """
    try:
        if date_str == "" or date_str is None:
            return None
        parts = date_str.split("-")
        if len(parts) != 3:
            return None
        year, month, day = parts

        # 修正 00 為 01
        month = "01" if month == "00" else month
        day = "01" if day == "00" else day

        clean_date = f"{year}-{month}-{day}"
        return datetime.strptime(clean_date, "%Y-%m-%d").date()
    except Exception:
        return None

# 取得Token
def get_access_token_KKBOX():
    url = "https://account.kkbox.com/oauth2/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Token 取得失敗: {response.status_code} - {response.text}")

def get_artist_KKBOX(artist_id, token):
    headers = {
        'accept': "application/json",
        'authorization': f"Bearer {token}"
    }

    url = f"{base_url}/artists/{artist_id}?territory=TW"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"查詢失敗: {response.text}")
    
    artist = response.json()
    return artist
    # print(f"藝人名稱: {artist['name']}")

# 查詢藝人專輯
def get_artist_albums_KKBOX(artist_id, token):
    headers = {
        'accept': "application/json",
        'authorization': f"Bearer {token}"
    }


    url = f"{base_url}/artists/{artist_id}/albums?territory=TW&limit=500"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"查詢專輯失敗: {response.text}")
    
    albums_data ={}

    albums = response.json()["data"]
    # print(albums)

    # return albums

    for album in albums:
        albums_data[album["id"]] = {
            "name": album["name"],
            # "album_type": album["album_type"],
            "release_date": parse_release_date(album["release_date"])
            # "release_date": album["release_date"]
        }

        # print(f"專輯名稱: {album['name']} - 發行日期: {album['release_date']}")

    sorted_albums = dict(sorted(
        albums_data.items(),
        key=lambda item: item[1]["release_date"],
        reverse=True
    ))

    return sorted_albums

    # for album_id, info in sorted_albums.items():
    #     print(f"{info['release_date']} - {info['name']}\t{album_id}")


# 主程式
if __name__ == "__main__":
    db = SessionLocal()
    artist_list = db.query(Artist).all()

    count = 1

    token = get_access_token_KKBOX()

    for user in artist_list:
        print(f"{count} - {user.name}")
        kkbox_ids = json.loads(user.kkbox_id) if user.kkbox_id else []

        for sid in kkbox_ids:
            artist_data = get_artist_KKBOX(sid, token)
            get_artist_albums_KKBOX(sid, token)

        print("=====================================")
        count += 1

    db.close()
