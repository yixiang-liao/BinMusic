# ingest_with_orm.py
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models.album import Album , Lyric
from app.db.models.news import News
from app.db.models.artists import Artist
from langchain_community.vectorstores import Chroma
from langchain.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain.text_splitter import CharacterTextSplitter
from tqdm import tqdm
from time import sleep
import os
# import torch

def split_documents(documents):
    print("✂️ 正在將長文件切割為多段...")
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    split_docs = []
    for doc in documents:
        split = text_splitter.split_documents([doc])
        split_docs.extend(split)
    print(f"� 切割後共有 {len(split_docs)} 筆子文件")
    return split_docs

def build_documents():
    db: Session = SessionLocal()
    documents = []

    # === 專輯 × 歌詞 × 藝人 ===

    # === 藝人資料 ===
    artists = db.query(Artist).all()
    for artist in artists:
        full_text = (
            f"【藝人名稱】{artist.name}\n"
            f"【英文名】{artist.en_name or ''}\n"
            f"【風格類型】{artist.genres}\n"
            f"【分類】{artist.type}\n\n"
            f"{artist.bin_intro or ''}"
        )
        documents.append(Document(
            page_content=full_text,
            metadata={
                "type": "artist",
                "name": artist.name,
                "id": f"artist-{artist.id}"
            }
        ))

    # === 新聞 ===
    news_list = db.query(News).filter(News.content != None).all()
    for news in news_list:
        full_text = (
            f"【新聞標題】{news.title}\n"
            f"【分類】{news.tag}\n"
            f"【日期】{news.date}\n\n"
            f"{news.content}"
        )
        documents.append(Document(
            page_content=full_text,
            metadata={
                "type": "news",
                "id": f"news-{news.id}",
                "title": news.title,
                "tag": news.tag,
                "date": news.date
            }
        ))

    db.close()
    return documents

def main():
    print("正在從 SQLite 讀取資料並建構語意文件...")
    docs = build_documents()
    print(f"總共建構 {len(docs)} 筆資料")
    docs = split_documents(docs)
    print(f"切割後共 {len(docs)} 筆子文件")

    embedding = HuggingFaceEmbeddings(
        model_name="shibing624/text2vec-base-chinese",
        model_kwargs={"device": "cuda"}  # 或改成 "cpu"
    )

    
    # embedding = OllamaEmbeddings(model="gemma:7b")

    print("� 使用 FAISS 向量資料庫建置中...")
    vectorstore = FAISS.from_documents(docs, embedding)
    vectorstore.save_local("./faiss_db_NEWS")

    print("✅ 向量資料完成並儲存！")
if __name__ == "__main__":
    main()