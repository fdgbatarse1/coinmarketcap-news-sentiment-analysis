from fastapi import FastAPI
from loguru import logger
from .scraper import scrape_coinmarketcap_news


app = FastAPI()


@app.get("/")
async def root():
    logger.debug("That's it, beautiful and simple logging!")
    return {"message": "Hello World"}


@app.get("/scrape-news")
async def scrape_news():
    """
    Endpoint to scrape CoinMarketCap news and return it as JSON.
    """
    logger.info("Scraping CoinMarketCap news...")
    news_data = scrape_coinmarketcap_news()
    return {"news": news_data}
