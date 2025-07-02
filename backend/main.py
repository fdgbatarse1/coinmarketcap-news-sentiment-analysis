from fastapi import FastAPI
from loguru import logger


app = FastAPI()


@app.get("/")
async def root():
    logger.debug("That's it, beautiful and simple logging!")
    return {"message": "Hello World"}