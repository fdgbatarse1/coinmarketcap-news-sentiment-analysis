import time
import os
import psycopg2
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from transformers import AutoTokenizer
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from backend.main import predict
from backend.src.models.models import TextIn

# Load environment variables from .env file
load_dotenv()

def get_db_connection():
    """Create a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            database=os.getenv("DB_NAME", "crypto_news"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres")
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def create_tables():
    """Create the necessary tables if they don't exist."""
    conn = get_db_connection()
    if not conn:
        return False

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS articles (
                        id SERIAL PRIMARY KEY,
                        url TEXT UNIQUE NOT NULL,
                        title TEXT NOT NULL,
                        author TEXT,
                        assets TEXT,
                        article_content TEXT,
                        prediction TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
        print("✅ Database tables ready")
        return True
    except Exception as e:
        print(f"Error creating tables: {e}")
        return False
    finally:
        conn.close()

def is_article_in_db(url):
    """Check if an article with the given URL already exists in the database."""
    conn = get_db_connection()
    if not conn:
        return False

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM articles WHERE url = %s", (url,))
                return cur.fetchone() is not None
    except Exception as e:
        print(f"Error checking article existence: {e}")
        return False
    finally:
        conn.close()

def save_article_to_db(article_data):
    """Save an article to the database."""
    conn = get_db_connection()
    if not conn:
        return False

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute('''
                    INSERT INTO articles (url, title, author, assets, article_content, prediction)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (
                    article_data['url'],
                    article_data['title'],
                    article_data['author'],
                    article_data['assets'],
                    article_data['article_content'],
                    article_data.get('prediction')  # Handle prediction if available
                ))
        return True
    except Exception as e:
        print(f"Error saving article: {e}")
        return False
    finally:
        conn.close()

def scrape_full_coinmarketcap_articles():
    """
    Scrapes news headlines from CoinMarketCap, then visits each article page
    to fetch the title, content, author, and associated assets using Selenium.
    """
    # Initialize database tables
    if not create_tables():
        print("⚠️ Could not initialize database tables. Continuing without database functionality.")

    headlines_url = "https://coinmarketcap.com/headlines/news/"

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    all_articles_data = []

    try:
        driver.get(headlines_url)
        time.sleep(3)

        page_soup = BeautifulSoup(driver.page_source, 'html.parser')
        article_links = []
        articles = page_soup.find_all('div', class_=lambda x: x and x.startswith('sc-4c05d6ef-0'))

        if not articles:
            print("No articles found. The website structure might have changed.")
            return

        print("--- Latest News from CoinMarketCap ---")

        for article in articles:
            a_tag = article.find('a', href=True)
            if a_tag:
                href = a_tag['href']
                if href:
                    full_url = href
                    if full_url.startswith("https://coinmarketcap.com"):
                        article_links.append(full_url)
        article_links = list(set(article_links))
        print(f"✅ Found {len(article_links)} articles. Fetching details for the first 3 as a demo...")
        for url in article_links[:3]:  # Limiting to 3 for demonstration
            # Check if article already exists in database
            if is_article_in_db(url):
                print(f"\n Article already saved: {url}")
                continue

            print(f"\n Scraping article: {url}")
            driver.get(url)

            try:
                article_soup = BeautifulSoup(driver.page_source, 'html.parser')
                title_element = article_soup.find('h1', class_='sc-21d469ac-7')
                title = title_element.get_text(strip=True) if title_element else "Title not found"

                author_element = article_soup.find(class_='sc-21d469ac-2 bmRJQj')
                author = author_element.get_text(strip=True) if author_element else "Author not found"

                content_container = article_soup.find(class_='sc-21d469ac-0')
                article_content = content_container.get_text(separator='\n',
                                                             strip=True) if content_container else "Content not found"

                asset_list = []

                asset_list = article_soup.find(class_='sc-65e7f566-0 fPdSKP base-text').get_text(strip=True)
                print(f"  - Title: {title}")
                print(f"  - Author: {author}")
                print(f"  - Assets: {asset_list if asset_list else 'No assets listed'}")
                print(f"  - Content: {article_content[:150]}...") # Printing a snippet

                article_data = {
                    'url': url,
                    'title': title,
                    'author': author,
                    'assets': asset_list,
                    'article_content': article_content
                }
                if is_article_in_db(url):
                    print("  ⚠️ Article already exists in database, skipping save.")
                    continue
                else:
                    model_dir = os.path.join('..', 'models', 'finbert_bitcoin_sentiment')
                    tokenizer = AutoTokenizer.from_pretrained(model_dir)

                    # Truncate the text before prediction
                    truncated_text = tokenizer.decode(
                        tokenizer.encode(
                            article_data['article_content'],
                            truncation=True,
                            max_length=512
                        ),
                        skip_special_tokens=True
                    )

                    # Use the truncated text for prediction
                    print(predict(TextIn(text=truncated_text)).label)
                    article_data["prediction"] = predict(TextIn(text=truncated_text)).label
                all_articles_data.append(article_data)

                # Save new article to database
                if save_article_to_db(article_data):
                    print("  ✅ New article saved to database")
                else:
                    print("  ⚠️ Failed to save article to database")

            except Exception as e:
                print(f"  ❌ Could not process article {url}. Reason: {e}")

    finally:
        driver.quit()

    return all_articles_data



if __name__ == "__main__":
    scraped_data = scrape_full_coinmarketcap_articles()
    print("\n--- Scraping Complete ---")
