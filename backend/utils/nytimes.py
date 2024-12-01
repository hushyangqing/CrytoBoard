from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from datetime import datetime
import time
import json

# Path to your ChromeDriver
CHROMEDRIVER_PATH = "./chromedriver-win64/chromedriver-win64/chromedriver.exe"

# Base URL for New York Times search
base_url = "https://www.nytimes.com/search"

# Cryptocurrency name mapping
CRYPTO_NAME_MAPPING = {
    'Bitcoin': 'BTC',
    'Ethereum': 'ETH',
    'Tether': 'USDT',
    'BNB': 'BNB',
    'Solana': 'SOL',
    'USDC': 'USDC',
    'XRP': 'XRP',
    'Dogecoin': 'DOGE',
    'TRON': 'TRX',
    'Toncoin': 'TON',
    'Cardano': 'ADA',
    'Shiba Inu': 'SHIB',
    'Avalanche': 'AVAX',
    'Bitcoin Cash': 'BCH',
    'Chainlink': 'LINK',
    'Polkadot': 'DOT',
    'UNUS SED LEO': 'LEO',
    'Sui': 'SUI',
    'Dai': 'DAI',
    'Litecoin': 'LTC',
}

# Function to convert date text into a Unix timestamp
def convert_date_to_timestamp(date_text):
    try:
        # Remove the period from abbreviated month names
        date_text = date_text.replace(".", "")
        # Parse the date text assuming format: "Nov 13" (after cleaning)
        parsed_date = datetime.strptime(date_text, "%b %d")  # Format for abbreviated months
        current_year = datetime.now().year
        parsed_date = datetime(current_year, parsed_date.month, parsed_date.day)
        return int(parsed_date.timestamp())
    except Exception as e:
        print(f"Error parsing date '{date_text}': {e}")
        return None


# Function to fetch search results
# Function to fetch search results
def fetch_articles(query, page=0):
    try:
        # Start Selenium WebDriver
        service = Service(CHROMEDRIVER_PATH)
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Run Chrome in headless mode
        driver = webdriver.Chrome(service=service, options=options)

        # Construct the URL with the query and pagination
        url = f"{base_url}?query={query}&page={page}"
        driver.get(url)
        time.sleep(1)  # Wait for the JavaScript to load
        # Use BeautifulSoup to parse the dynamically loaded content
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()

        articles = []

        # Parse articles
        for item in soup.find_all('li', {'data-testid': 'search-bodega-result'}):  # Target each result
            title_tag = item.find('h4')
            headline_tag = item.find('p', class_='css-16nhkrn')  # Updated to target the specific headline class
            date_tag = item.find('span', class_='css-17ubb9w')  # Locate the date span
            link_tag = item.find('a', href=True)
            image_tag = item.find('img')  # Locate the image tag

            if title_tag and link_tag:
                title = title_tag.get_text(strip=True)
                headline = headline_tag.get_text(strip=True) if headline_tag else "No headline available"  # Updated logic
                link = "https://www.nytimes.com" + link_tag['href']

                # Extract image URL if available
                image_url = image_tag['src'] if image_tag and image_tag.get('src') else "No image available"

                # Convert date to Unix timestamp
                timestamp = None
                if date_tag:
                    date_text = date_tag.get_text(strip=True)  # Extract the date text (e.g., "August 5")
                    if date_text:
                        timestamp = convert_date_to_timestamp(date_text)

                # Count cryptocurrency occurrences in the title and headline
                crypto_counts = count_crypto_occurrences(f"{title} {headline}")

                # Only include articles with non-empty crypto_counts
                if crypto_counts:
                    articles.append({
                        "title": title,
                        "headline": headline,
                        "timestamp": timestamp,
                        "crypto_counts": crypto_counts,
                        "image_url": image_url,
                        "source_url": link  # Add source URL here
                    })
        return articles
    except Exception as e:
        print(f"Error fetching articles: {e}")
        return []


# Function to count occurrences of cryptocurrencies
def count_crypto_occurrences(text):
    counts = {}
    for name, symbol in CRYPTO_NAME_MAPPING.items():
        name_count = text.lower().count(name.lower())
        symbol_count = text.lower().count(symbol.lower())
        total_count = name_count + symbol_count
        if total_count > 0:
            counts[symbol] = total_count
    return counts

# Main function
def main():
    query = "cryptocurrency"
    all_articles = []
    max_pages = 20  # Set the maximum number of pages to scrape

    for page in range(max_pages):
        print(f"Fetching page {page + 1}...")
        articles = fetch_articles(query, page=page)
        if not articles:
            print(f"No articles found on page {page + 1}.")
            break
        all_articles.extend(articles)

    # Save results to a JSON file
    with open("nyt_crypto_articles_filtered.json", "w", encoding="utf-8") as file:
        json.dump(all_articles, file, ensure_ascii=False, indent=4)

    print(f"\nSaved {len(all_articles)} articles to 'nyt_crypto_articles_filtered.json'.")

if __name__ == "__main__":
    main()
