from pydantic import BaseModel


class TextIn(BaseModel):
    text: str

class SentimentOut(BaseModel):
    label: str
    score: float