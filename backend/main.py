from fastapi import FastAPI
from loguru import logger
from src.routers import fine_tuning

app = FastAPI()

app.include_router(fine_tuning.router)


@app.get("/")
async def root():
    logger.debug("That's it, beautiful and simple logging!")
    return {"message": "Hello World"}
