import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.models.news import News
from ckip_transformers.nlp import CkipWordSegmenter, CkipPosTagger, CkipNerChunker
import json

ws_driver = CkipWordSegmenter(model="albert-tiny")
pos_driver = CkipPosTagger(model="albert-tiny")
ner_driver = CkipNerChunker(model="albert-tiny")

def analyze_with_ckip(text: str):
    ws = ws_driver([text])[0]
    pos = pos_driver([ws])[0]
    ner = ner_driver([text])[0]

    return {
        "ws_result": json.dumps(ws, ensure_ascii=False),
        "pos_result": json.dumps(pos, ensure_ascii=False),
        "ner_result": json.dumps([[e[0], e[1], e[2]] for e in ner], ensure_ascii=False)
    }

def crawl_binmusic_news(db: Session):
    base_url = "https://www.bin-music.com.tw/news"
    user_agent = UserAgent()

    # 模擬抓首頁取得總頁數
    req = requests.get(base_url, headers={ 'user-agent': user_agent.random }, timeout=5)
    soup = BeautifulSoup(req.text, 'lxml')
    pages = int(soup.find('li', {'class': "info"}).text[-3:])

    new_entries = []

    for page in range(1, pages + 1):
        page_url = f"{base_url}/p{page}"
        res = requests.get(page_url, headers={ 'user-agent': user_agent.random }, timeout=5)
        soup_page = BeautifulSoup(res.text, 'lxml')
        blocks = soup_page.find_all('div', {'class': "two-col"})

        for block in blocks:
            title = block.find('div', class_='title').text.strip()
            date = block.find('div', class_='date').text.strip()
            date_obj = datetime.strptime(date, "%Y.%m.%d")
            link = block.find('a')['href']
            full_link = f"https://www.bin-music.com.tw{link}" if link.startswith('/') else link
            news_id = int(full_link[-4:])

            # 如果資料庫已有此 ID，跳過
            if db.query(News).filter(News.id == news_id).first():
                continue

            content_page = requests.get(full_link, headers={ 'user-agent': user_agent.random }, timeout=5)
            content_soup = BeautifulSoup(content_page.text, 'lxml')
            img = content_soup.find('img' , class_='mobile')['src']
            content = ''.join(p.text.strip() for p in content_soup.find_all('p'))

            tag_div = content_soup.find('div', class_='tag')
            tags = ','.join(a.text.strip() for a in tag_div.find_all('a')) if tag_div else ''

            analysis = analyze_with_ckip(content)

            news_item = News(
                id=news_id,
                tag=tags,
                title=title,
                date=date_obj.strftime("%Y-%m-%d"),
                link=full_link,
                image=img,
                content=content,
                ws_result=analysis["ws_result"],
                pos_result=analysis["pos_result"],
                ner_result=analysis["ner_result"]
            )
            db.add(news_item)
            new_entries.append(news_item)

    db.commit()
    return new_entries  # 回傳新增資料給向量庫處理
