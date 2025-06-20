from fastapi import FastAPI
from app.api.v1.endpoints.artist import artist_Basic_Information , artist
from app.api.v1.endpoints.rag import rag_response
from app.api.v1.endpoints.news import news_api , news 
from app.api.v1.endpoints import album , lyric_feedback
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

# 加入 CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⛔️ 正式上線時請改為指定網址，例如 ["https://your-frontend.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(artist_Basic_Information.router, prefix="/api/v1", tags=["artists"])
app.include_router(artist.router, prefix="/api/v1", tags=["artists"])
app.include_router(rag_response.router, prefix="/api/v1/rag", tags=["rag"])
app.include_router(news_api.router, prefix="/api/v1/news", tags=["news"])
app.include_router(news.router, prefix="/api/v1/news", tags=["news"])
app.include_router(album.router, prefix="/api/v1/album", tags=["album"])
app.include_router(lyric_feedback.router, prefix="/api/v1/lyric_feedback", tags=["lyric_feedback"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)