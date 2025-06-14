from sqlalchemy.orm import Session
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from db.session import SessionLocal
from db.model.album import Lyric , Album , LyricLine
from db.model.artists import Artist

# 1. 載入模型（支援繁體）
model_name = "IDEA-CCNL/Erlangshen-Roberta-110M-Sentiment"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# 2. 情緒標籤對應（模型輸出為 [負面, 中性, 正面]）
id2label = {0: "negative", 1: "neutral", 2: "positive"}

# 3. 預測情緒分數（回傳正面機率 + 分類）
def get_emotion_prediction(text: str):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        logits = model(**inputs).logits
    probs = torch.softmax(logits, dim=-1)[0]
    label_id = torch.argmax(probs).item()

    # 🧠 根據類別數決定輸出
    if len(probs) == 3:
        return round(probs[2].item(), 4), id2label[label_id]  # 正面機率 + 標籤
    elif len(probs) == 2:
        return round(probs[1].item(), 4), ["negative", "positive"][label_id]  # 二分類 fallback
    else:
        raise ValueError("不支援的類別數: {}".format(len(probs)))


# 4. 更新情緒資料到資料庫
def update_emotion_scores():
    db: Session = SessionLocal()
    lyrics = db.query(Lyric).all()
    count = 0

    for lyric in lyrics:
        if lyric.lyrics:
            try:
                score, label = get_emotion_prediction(lyric.lyrics)
                lyric.emotion_score = score
                lyric.emotion_label = label
                count += 1
                print(f"[{count}] {lyric.title} -> {label} ({score})")
            except Exception as e:
                print(f"[Error] {lyric.title}: {e}")

    db.commit()
    db.close()
    print(f"✅ Done. Updated {count} lyrics.")

# 5. 執行
if __name__ == "__main__":
    update_emotion_scores()