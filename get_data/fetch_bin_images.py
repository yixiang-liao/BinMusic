import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from db.session import SessionLocal
from db.model.artists import Artist
from db.model.album import Album

def extract_cover_image_url(bin_url: str) -> str:
    try:
        response = requests.get(bin_url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # 優先找 .cover.artist
        cover_div = soup.find("div", class_="cover artist")
        if not cover_div:
            # 備援找 .cover.artist.no-animation
            cover_div = soup.find("div", class_="cover artist no-animation")

        if not cover_div:
            print(f"⚠️ 找不到封面元素: {bin_url}")
            return None

        data_bg = cover_div.get("data-bg", "")
        if "url(" in data_bg:
            img_url = data_bg.split("url(")[-1].split(")")[0].strip('"').strip("'")
            return img_url
        else:
            print(f"⚠️ data-bg 格式不正確: {bin_url}")
            return None

    except Exception as e:
        print(f"❌ 錯誤讀取 {bin_url}: {e}")
        return None

def main():
    db: Session = SessionLocal()
    artists = db.query(Artist).filter(Artist.bin_url.isnot(None)).all()

    print(f"🎵 共取得 {len(artists)} 位有 bin_url 的藝人")

    updated = 0
    for artist in artists:
        print(f"\n🔍 處理: {artist.name} - {artist.bin_url}")
        img_url = extract_cover_image_url(artist.bin_url)

        if img_url:
            print(f"✅ 封面圖連結: {img_url}")
            artist.bin_img = img_url
            db.commit()
            updated += 1
        else:
            print("❌ 無法取得封面圖")

    print(f"\n✅ 更新完成，共成功寫入 {updated} 筆 bin_img")

if __name__ == "__main__":
    main()