from datetime import datetime, timedelta
from airflow import DAG

import sys
import os

from airflow.decorators import task
# Add the project root directory to the Python path to import the scraper
sys.path.append(os.path.dirname(__file__))





from tasks.scraper import scrape_full_coinmarketcap_articles



# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 7, 17),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Create the DAG
dag = DAG(
    'coinmarketcap_scraper',
    default_args=default_args,
    description='A DAG to scrape CoinMarketCap articles hourly',
    schedule_interval='@hourly',
    catchup=False,
)

@task(task_id="scrape_full_coinmarketcap_articles", dag=dag)
def scrape_coinmarketcap_articles():
    """
    Task to scrape full articles from CoinMarketCap.
    This function will be executed by the Airflow DAG.
    """
    scrape_full_coinmarketcap_articles()


if __name__ == "__main__":
    scrape_coinmarketcap_articles()
