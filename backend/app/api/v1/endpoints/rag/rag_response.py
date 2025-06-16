from functools import lru_cache
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.artists import Artist
from app.db.models.album import Album , Lyric , LyricLine
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from app.schemas.rag.rag_response import AskRequest , AskResponse
from pathlib import Path
from fastapi.responses import StreamingResponse
from huggingface_hub import InferenceClient
import asyncio
from app.core.config import Settings
from collections import defaultdict
import json



VECTOR_DB_PATH = (Path(__file__).parent / "faiss_db_album_V2").resolve()        # path to your FAISS index directory
VECTOR_DB_PATH_NEWS = (Path(__file__).parent / "faiss_db_NEWS").resolve()        # path to your FAISS index directory
EMBEDDING_MODEL = "shibing624/text2vec-base-chinese"
LLM_MODEL = "gemma3:4b-it-qat"                          # change if you prefer another Ollama model
TOP_K = 10                                       # number of passages to retrieve

router = APIRouter()

@lru_cache(maxsize=1)
def _get_embeddings():
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

# 專輯向量資料庫與 retriever
@lru_cache(maxsize=1)
def _get_vectorstore_album():
    return FAISS.load_local(VECTOR_DB_PATH, _get_embeddings(), allow_dangerous_deserialization=True)

@lru_cache(maxsize=1)
def _get_retriever_album():
    return _get_vectorstore_album().as_retriever(search_kwargs={"k": TOP_K})

# 新聞向量資料庫與 retriever
@lru_cache(maxsize=1)
def _get_vectorstore_news():
    return FAISS.load_local(VECTOR_DB_PATH_NEWS, _get_embeddings(), allow_dangerous_deserialization=True)

@lru_cache(maxsize=1)
def _get_retriever_news():
    return _get_vectorstore_news().as_retriever(search_kwargs={"k": TOP_K})



@lru_cache(maxsize=1)
def _get_llm_chain():
    prompt_template = (
        """
        請根據以下資料，用繁體中文詳細回答問題。
        如果資料中沒有提及，請回答「資料中未提及」。
        =========\n{context}\n=========
        \n問題：{question}
        """
    )
    prompt = PromptTemplate(
        input_variables=["context", "question"], template=prompt_template
    )
    llm = OllamaLLM(model=LLM_MODEL, streaming=True)
    return LLMChain(prompt=prompt, llm=llm)

@lru_cache(maxsize=1)
def _get_llm_chain＿NEWS():
    # prompt_template = ("""
    #     你是一位台灣流行音樂知識庫的小編，擅長整合資料並清楚回答問題。

    #     根據以下資料，請總合整理並用繁體中文有條理地回答問題。
    #     若資料中未提及，請明確指出「資料中未提及」，不要臆測。

    #     ========= 資料開始 =========
    #     {context}
    #     ========= 資料結束 =========

    #     問題：{question}

    #     請詳細作答：
    #     """
    # )
    prompt_template = ("""
        你是一位台灣流行音樂知識庫的小編，擅長整合資料並清楚回答問題。

        根據以下資料，請總合整理並用繁體中文有條理地回答問題。

        ========= 資料開始 =========
        {context}
        ========= 資料結束 =========

        問題：{question}

        請詳細作答：
        """
    )
    prompt = PromptTemplate(
        input_variables=["context", "question"], template=prompt_template
    )
    llm = OllamaLLM(model=LLM_MODEL, streaming=True)
    return LLMChain(prompt=prompt, llm=llm)

@router.get("/health", summary="健康檢查")
async def health_check():
    return {"status": "ok"}

@router.post("/stream/ask/album", summary="串流回答專輯")
async def ask_stream_album(req: AskRequest):
    retriever = _get_retriever_album()
    llm_chain = _get_llm_chain()

    docs = retriever.get_relevant_documents(req.question)

    # 整理來源
    sources = [
        {
            "title": doc.metadata.get("title", "未知標題"),
            "content": doc.page_content[:200]  # 節錄前段文字
        }
        for doc in docs
    ]

    print("🔍 [ALBUM] 檢索到的文件（原始段落）:")
    for i, doc in enumerate(docs, 1):
        print(f"--- Document {i} ---")
        print(f"parent_id: {doc.metadata.get('parent_id')}")
        print(f"title: {doc.metadata.get('title', 'N/A')}")
        print(f"內容:\n{doc.page_content}")
        print(doc.page_content[:500], "\n")

    context = "\n\n".join(doc.page_content for doc in docs)

    async def token_stream():
        # 回傳來源資料（type: source）
        yield json.dumps({
            "type": "source",
            "data": sources
        }) + "\n"

        # 串流回答內容（type: answer）
        async for chunk in llm_chain.astream({"context": context, "question": req.question}):
            yield json.dumps({
                "type": "answer",
                "data": chunk["text"]
            }) + "\n"
            await asyncio.sleep(0.01)

    return StreamingResponse(token_stream(), media_type="text/plain")


@router.post("/stream/ask/news", summary="串流回答新聞相關")
async def ask_stream_news(req: AskRequest):
    retriever = _get_retriever_news()
    llm_chain = _get_llm_chain_NEWS()

    docs = retriever.get_relevant_documents(req.question)

    print("🔍 [NEWS] 檢索到的文件（原始段落）:")
    for i, doc in enumerate(docs, 1):
        print(f"--- Document {i} ---")
        print(f"parent_id: {doc.metadata.get('parent_id')}")
        print(f"title: {doc.metadata.get('title', 'N/A')}")
        print(f"內容:\n{doc.page_content[:300]}...\n")  # 最多印前段

    # 提取來源資訊
    sources = [
        {
            "title": doc.metadata.get("title", "未知標題"),
            "content": doc.page_content[:200]  # 僅節錄前段文字
        }
        for doc in docs
    ]

    # 整合 context
    context = "\n\n".join(doc.page_content for doc in docs)

    async def token_stream():
        # 回傳來源資訊（一次）
        yield json.dumps({
            "type": "source",
            "data": sources
        }) + "\n"

        # 串流回傳回答文字
        async for chunk in llm_chain.astream({
            "context": context,
            "question": req.question
        }):
            yield json.dumps({
                "type": "answer",
                "data": chunk["text"]
            }) + "\n"
            await asyncio.sleep(0.01)

    return StreamingResponse(token_stream(), media_type="application/json")