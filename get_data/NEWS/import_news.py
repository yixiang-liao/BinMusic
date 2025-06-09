import pandas as pd
from sqlalchemy.orm import Session
from db.model.news import News
from db.base import Base ,engine, SessionLocal

# 載入 CSV
df = pd.read_csv("./NEWS/binmusic_news.csv")

# 建立 Session
session: Session = SessionLocal()

# 匯入每一筆資料
for _, row in df.iterrows():
    news = News(
        id=int(row["ID"]),
        tag=row["Tag"],
        title=row["Title"],
        date=row["Date"],
        link=row["Link"],
        image=row["Image"],
        content=row["Content"],
        ws_result=row["ws_result"],
        pos_result=row["pos_result"],
        ner_result=row["ner_result"]
    )
    session.merge(news)  # merge 可避免重複插入
session.commit()
session.close()

print("✅ CSV 資料已匯入 news 資料表！")
