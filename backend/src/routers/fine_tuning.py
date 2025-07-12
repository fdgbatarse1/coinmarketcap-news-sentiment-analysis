from fastapi import APIRouter, BackgroundTasks
from src.tasks.sentiment_analysis import sentiment_analysis

router = APIRouter()


@router.post("/fine-tuning")
def fine_tuning(background_tasks: BackgroundTasks):
    background_tasks.add_task(sentiment_analysis)
    return {"message": "Fine-tuning model"}
