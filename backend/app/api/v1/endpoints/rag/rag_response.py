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


# client = InferenceClient(model="google/gemma-7b-it", token="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")
client = InferenceClient(model="HuggingFaceH4/zephyr-7b-beta", token="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")
# client = InferenceClient(model="openai-community/gpt2", token="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")


VECTOR_DB_PATH = (Path(__file__).parent / "faiss_db_album").resolve()        # path to your FAISS index directory
EMBEDDING_MODEL = "shibing624/text2vec-base-chinese"
LLM_MODEL = "gemma:2b"                          # change if you prefer another Ollama model
TOP_K = 5                                       # number of passages to retrieve

router = APIRouter()

@lru_cache(maxsize=1)
def _get_embeddings():
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


@lru_cache(maxsize=1)
def _get_vectorstore():
    return FAISS.load_local(
        VECTOR_DB_PATH,
        _get_embeddings(),
        allow_dangerous_deserialization=True,
    )


@lru_cache(maxsize=1)
def _get_retriever():
    return _get_vectorstore().as_retriever(search_kwargs={"k": TOP_K})


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

@router.post("/ask", response_model=AskResponse, summary="向 RAG 系統提問")
async def ask(req: AskRequest):
    """RAG QA endpoint – returns answer + top‑k contexts (as plain text)."""
    retriever = _get_retriever()
    llm_chain = _get_llm_chain()

    try:
        docs = retriever.get_relevant_documents(req.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"檢索資料庫時發生錯誤: {e}")

    context = "\n\n".join(doc.page_content for doc in docs)

    try:
        answer = llm_chain.run({"context": context, "question": req.question})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM 生成回答時發生錯誤: {e}")

    # 簡單整理來源：若 metadata 中有 'source' 就帶出，否則取前 30 字
    sources = [
        (doc.metadata.get("source") or doc.page_content[:30]).strip() for doc in docs
    ]

    return AskResponse(answer=answer, sources=sources)


@router.get("/health", summary="健康檢查")
async def health_check():
    return {"status": "ok"}

@router.post("/ask/stream", summary="串流回答")
async def ask_stream(req: AskRequest):
    retriever = _get_retriever()
    llm_chain = _get_llm_chain()

    docs = retriever.get_relevant_documents(req.question)
    context = "\n\n".join(doc.page_content for doc in docs)

    # 建立 generator
    async def token_stream():
        async for chunk in llm_chain.astream({"context": context, "question": req.question}):
            yield chunk["text"]  # or chunk.delta for per-token
            await asyncio.sleep(0.01)  # 避免過快造成瀏覽器不顯示

    return StreamingResponse(token_stream(), media_type="text/plain")

@router.post("/ask/hf_stream", summary="使用 Hugging Face 模型串流回答")
async def ask_hf_stream(req: AskRequest):
    retriever = _get_retriever()
    docs = retriever.get_relevant_documents(req.question)
    context = "\n\n".join(doc.page_content for doc in docs)

    full_prompt = f"""請用繁體中文回答以下問題。\n\n已知內容：\n=========\n{context}\n=========\n\n問題：{req.question}"""

    def generate():
        try:
            for chunk in client.text_generation(full_prompt, stream=True, max_new_tokens=512):
                yield chunk
        except Exception as e:
            yield f"[錯誤] {e}"

    return StreamingResponse(generate(), media_type="text/plain")