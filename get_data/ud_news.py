import json
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from db.model.news import News
from db.base import Base ,engine, SessionLocal

def fix_ws_result_format(db: Session):
    all_news = db.query(News).all()
    count = 0

    for news in all_news:
        try:
            # 如果已經是 JSON list，跳過
            current = json.loads(news.ws_result)
            if isinstance(current, list):
                continue
        except Exception:
            pass  # 不是 JSON list，繼續處理

        # 如果 ws_result 是用空格分隔的斷詞（例如 "靈魂 DIVA 家家 睽違..."），轉成 list
        if news.ws_result and isinstance(news.ws_result, str):
            tokens = news.ws_result.strip().split()
            news.ws_result = json.dumps(tokens, ensure_ascii=False)
            count += 1

    db.commit()
    print(f"✅ 更新完成，共修正 {count} 筆 ws_result。")

if __name__ == "__main__":
    db: Session = SessionLocal()
    fix_ws_result_format(db)
    db.close()
