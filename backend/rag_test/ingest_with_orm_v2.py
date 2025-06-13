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

    # 1. 專輯 × 全部歌詞 × 藝人
    albums = db.query(Album).join(Artist).all()
    for album in albums:
        artist = album.artist
        lyrics = db.query(Lyric).filter(Lyric.album_id == album.id).all()

        if not lyrics:
            continue

        all_lyrics_text = ""
        for lyric in lyrics:
            if lyric.lyrics:
                all_lyrics_text += f"\n【歌曲】{lyric.title}\n【歌詞】\n {lyric.lyrics}\n"

        combined_text = (
            f"【專輯名稱】{album.album_name}\n"
            f"【發行日期】{album.release_date}\n"
            f"【專輯類型】{album.album_type}\n"
            f"【專輯介紹】{album.description or '無'}\n"
            f"【歌曲總數】{album.total_tracks}\n"
            f"【藝人】{artist.name}\n"
            f"\n=== 專輯歌曲與歌詞 ===\n"
            f"{all_lyrics_text.strip()}"
        )

        documents.append(Document(
            page_content=combined_text,
            metadata={
                "type": "album",
                "album": album.album_name,
                "artist": artist.name,
                "id": f"album-{album.id}"
            }
        ))

    

    db.close()
    return documents

def main():
    print("� 正在從 SQLite 讀取資料並建構語意文件...")
    docs = build_documents()
    print(f"� 總共建構 {len(docs)} 筆資料")
    docs = split_documents(docs)
    print(f"� 切割後共 {len(docs)} 筆子文件")

    embedding = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cuda"}  # 或改成 "cpu"
    )

    
    # embedding = OllamaEmbeddings(model="gemma:7b")

    print("� 使用 FAISS 向量資料庫建置中...")
    vectorstore = FAISS.from_documents(docs, embedding)
    vectorstore.save_local("./faiss_db_ollama")

    print("✅ 向量資料完成並儲存！")

# def main():
#     print("� 正在從 SQLite 讀取資料並建構語意文件...")
#     docs = build_documents()
#     print(f"� 總共建構 {len(docs)} 筆資料")
#     docs = split_documents(docs)
#     print(f"� V2總共建構 {len(docs)} 筆資料")
#     # os.environ["OLLAMA_NUM_GPU"] = "0"  # 強制用 CPU

#     # 顯示 CUDA 狀態
#     # if torch.cuda.is_available():
#     #     print(f"� CUDA 可用！GPU: {torch.cuda.get_device_name(0)}")
#     # else:
#     #     print("⚠️ CUDA 不可用，將使用 CPU")

#     print("� 建立 Chroma 向量資料庫，使用 Gemma 7b Embedding...")
#     # embedding = OllamaEmbeddings(model="gemma:7b")
#     embedding = HuggingFaceEmbeddings(
#         model_name="sentence-transformers/all-MiniLM-L6-v2",
#         model_kwargs={"device": "cuda"}  # 改成 "cuda" 若你未來要用 GPU
#     )
#     print("� 初始化 Chroma 向量資料庫")
#     # vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embedding)
#     vectorstore = FAISS.from_documents(docs, embedding)

#     print("� 分批加入向量庫，每批 100 筆...")
#     # BATCH_SIZE = 100
#     # for i in tqdm(range(0, len(docs), BATCH_SIZE)):
#     #     batch = docs[i:i + BATCH_SIZE]
#     #     try:
#     #         vectorstore.add_documents(batch)
#     #         vectorstore.persist()
#     #     except Exception as e:
#     #         print(f"⚠️ 第 {i}-{i+BATCH_SIZE} 批失敗: {e}")
#     for i in tqdm(range(len(docs))):
#         batch = docs[i]
#         print(f"� 正在處理第 {i} 筆資料...")
#         print(batch)
#         try:
#             vectorstore.add_documents([batch])
#             vectorstore.persist()
#         except Exception as e:
#             print(f"⚠️ 第 {i} 批失敗: {e}")
#         # sleep(1)

#     print("✅ 成功完成所有資料餵入並儲存向量資料庫！")

if __name__ == "__main__":
    main()