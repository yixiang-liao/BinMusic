from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.news_spider import crawl_binmusic_news
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain.text_splitter import CharacterTextSplitter
from pathlib import Path

router = APIRouter()
VECTOR_DB_PATH_NEWS = Path(__file__).parent / "../rag/faiss_db_NEWS"
embedding = HuggingFaceEmbeddings(model_name="shibing624/text2vec-base-chinese")

def split_documents(documents):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    split_docs = []
    for doc in documents:
        chunks = text_splitter.split_text(doc.page_content)
        for i, chunk in enumerate(chunks):
            split_docs.append(Document(
                page_content=chunk,
                metadata={**doc.metadata, "chunk_index": i}
            ))
    return split_docs

@router.post("/crawl/news", summary="爬蟲並更新新聞與向量庫")
def crawl_news_and_update_vectorstore(db: Session = Depends(get_db)):
    new_items = crawl_binmusic_news(db)

    if not new_items:
        return {"message": "沒有新資料"}

    # Step 1: 建立完整 Document，包含 parent_id
    docs = []
    for item in new_items:
        full_text = (
            f"【新聞標題】{item.title}\n"
            f"【分類】{item.tag}\n"
            f"【日期】{item.date}\n\n"
            f"{item.content}"
        )

        docs.append(Document(
            page_content=full_text,
            metadata={
                "type": "news",
                "id": f"news-{item.id}",
                "parent_id": f"news-{item.id}",   # ✅ 加上這行才不會 None！
                "title": item.title,
                "tag": item.tag,
                "date": item.date,
                "content": item.content
            }
        ))

    # Step 2: 切割為 chunks 並保留 metadata + chunk_index
    split_docs = split_documents(docs)

    # Step 3: 寫入向量庫
    vectorstore = FAISS.load_local(str(VECTOR_DB_PATH_NEWS), embedding, allow_dangerous_deserialization=True)
    vectorstore.add_documents(split_docs)
    vectorstore.save_local(str(VECTOR_DB_PATH_NEWS))

    return {
        "message": f"成功新增 {len(new_items)} 筆新聞資料",
        "chunks": len(split_docs)
    }
