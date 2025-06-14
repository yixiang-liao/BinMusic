from sqlalchemy.orm import Session
from sqlalchemy import select
from db.model.news import News
from db.session import SessionLocal
from ckip_transformers.nlp import CkipWordSegmenter, CkipPosTagger, CkipNerChunker
from tqdm import tqdm
import json
import time

# 初始化 CKIP 模型
ws_driver = CkipWordSegmenter(model="albert-tiny")
pos_driver = CkipPosTagger(model="albert-tiny")
ner_driver = CkipNerChunker(model="albert-tiny")

BATCH_SIZE = 25

def reprocess_news_batch_nlp():
    db: Session = SessionLocal()
    news_items = db.execute(select(News)).scalars().all()
    total = len(news_items)

    print(f"🔁 共 {total} 筆新聞，每 {BATCH_SIZE} 筆一起送 CKIP 分析")

    for i in tqdm(range(0, total, BATCH_SIZE), desc="處理進度"):
        batch = news_items[i:i + BATCH_SIZE]
        texts = [(item.title or "") + "\n" + (item.content or "") for item in batch]

        try:
            ws = ws_driver(texts)
            pos = pos_driver(ws)
            ner = ner_driver(ws)

            for j, item in enumerate(batch):
                item.ws_result = json.dumps(ws[j], ensure_ascii=False)
                item.pos_result = json.dumps(pos[j], ensure_ascii=False)
                item.ner_result = json.dumps(ner[j], ensure_ascii=False)

            db.commit()
            time.sleep(1.5)  # 可選：降低 API 負載

        except Exception as e:
            print(f"❌ [第 {i} ~ {i + BATCH_SIZE} 筆] 分析錯誤：{e}")

    db.close()
    print("🎉 全部處理完畢！")

# 執行
if __name__ == "__main__":
    reprocess_news_batch_nlp()
