from fastapi import FastAPI
from app.api.v1.endpoints.artist import artist_Basic_Information


app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(artist_Basic_Information.router, prefix="/api/v1", tags=["artists"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)