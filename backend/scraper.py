import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


def scrape_full_coinmarketcap_articles():
    """
    Scrapes news headlines from CoinMarketCap, then visits each article page
    to fetch the title, content, author, and associated assets using Selenium.
    """
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

        print(f"✅ Found {len(article_links)} articles. Fetching details for the first 3 as a demo...")

        for url in article_links[:3]:  # Limiting to 3 for demonstration
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

                all_articles_data.append({
                    'url': url,
                    'title': title,
                    'author': author,
                    'assets': asset_list,
                    'article_content': article_content
                })

            except Exception as e:
                print(f"  ❌ Could not process article {url}. Reason: {e}")

    finally:
        driver.quit()

    return all_articles_data



scraped_data = scrape_full_coinmarketcap_articles()
print("\n--- Scraping Complete ---")
