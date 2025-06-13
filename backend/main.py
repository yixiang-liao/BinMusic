from fastapi import FastAPI
from app.api.v1.endpoints.artist import artist_Basic_Information
from app.api.v1.endpoints.rag import rag_response
from app.api.v1.endpoints.news import news_api


app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(artist_Basic_Information.router, prefix="/api/v1", tags=["artists"])
app.include_router(rag_response.router, prefix="/api/v1/rag", tags=["rag"])
app.include_router(news_api.router, prefix="/api/v1/news", tags=["news"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)