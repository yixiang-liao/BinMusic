from pydantic import BaseModel , Field
from typing import Optional , List


class AskRequest(BaseModel):
    question: str = Field(..., example="可以推薦給我幾首浪漫的歌曲嗎，並說明推薦的原因")


class AskResponse(BaseModel):
    answer: str
    sources: List[str]