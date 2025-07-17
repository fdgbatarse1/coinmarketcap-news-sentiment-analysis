from fastapi import FastAPI
from loguru import logger
from backend.src.models.models import SentimentOut, TextIn
from src.routers import fine_tuning
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import os

app = FastAPI()

app.include_router(fine_tuning.router)
model_dir =  os.path.join('..', 'models', 'finbert_bitcoin_sentiment_pretrained')
tokenizer = AutoTokenizer.from_pretrained(model_dir)
model = AutoModelForSequenceClassification.from_pretrained(model_dir)

sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model=model,
    tokenizer=tokenizer,
    device=0
)

@app.get("/")
async def root():
    logger.debug("That's it, beautiful and simple logging!")
    return {"message": "Hello World"}


@app.post("/predict", response_model=SentimentOut)
def predict(payload: TextIn):
    result = sentiment_pipeline(payload.text)[0]
    return SentimentOut(label=result["label"], score=result["score"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)