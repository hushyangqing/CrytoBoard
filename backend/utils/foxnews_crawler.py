import requests
from bs4 import BeautifulSoup
from collections import Counter
import time
import datetime
import json
import re
from dateutil import parser

# Define the target cryptocurrencies
crypto_currencies = {'BTC', 'ETH', 'USDT', 'BNB', 'SOL', 'USDC', 'XRP', 'DOGE', 
                     'TRX', 'TON', 'ADA', 'SHIB', 'AVAX', 'BCH', 'LINK', 'DOT', 
                     'LEO', 'SUI', 'DAI', 'LTC'}

# Target URL
base_url = "https://www.foxbusiness.com/category/cryptocurrency"

# Expanded timezone information for common abbreviations
tzinfos = {
    "EST": -5 * 3600,  # Eastern Standard Time
    "EDT": -4 * 3600,  # Eastern Daylight Time
    "CST": -6 * 3600,  # Central Standard Time
    "CDT": -5 * 3600,  # Central Daylight Time
    "MST": -7 * 3600,  # Mountain Standard Time
    "MDT": -6 * 3600,  # Mountain Daylight Time
    "PST": -8 * 3600,  # Pacific Standard Time
    "PDT": -7 * 3600,  # Pacific Daylight Time
    "GMT": 0,           # Greenwich Mean Time
    "UTC": 0,           # Coordinated Universal Time
}

# Function to get article links
def get_article_links(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3' }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Unable to access page: {url}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('article')
    links = []
    for article in articles:
        link = article.find('a', href=True)
        if link:
            href = link['href']
            if 'video' not in href.lower():
                full_url = href if href.startswith("http") else "https://www.foxbusiness.com" + href
                links.append(full_url)
    return links

# Function to clean text and replace Unicode characters
def clean_text(text):
    text = re.sub(r'[\n\xa0]+', ' ', text).strip()
    text = text.replace('\u2018', "'").replace('\u2019', "'")
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    return text

# Function to parse and convert time format to Unix timestamp
def parse_time(time_text):
    try:
        dt = parser.parse(time_text, tzinfos=tzinfos)
        return int(dt.timestamp())
    except Exception as e:
        print(f"Error parsing time '{time_text}': {e}")
        return None

# Function to analyze article content and extract information
# Function to analyze article content and extract information
def analyze_article(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3' }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Unable to access article: {url}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    title = clean_text(soup.find('h1').get_text() if soup.find('h1') else "No title")
    headline = clean_text(soup.find('h2', class_='sub-headline').get_text() if soup.find('h2', class_='sub-headline') else "No headline")
    
    if "Log in to comment on videos" in headline:
        print(f"Skipped video page: {url}")
        return None

    time_tag = soup.find('time', class_='article-date__time')
    timestamp = parse_time(time_tag.get_text().strip()) if time_tag else None

    paragraphs = soup.find_all('p')
    article_text = ' '.join([para.get_text() for para in paragraphs])

    crypto_counts = {currency: article_text.lower().count(currency.lower()) for currency in crypto_currencies}
    crypto_counts = {currency: count for currency, count in crypto_counts.items() if count > 0}

    # Find the first <img> under the <picture> tag
    picture_tag = soup.find('picture')
    img_url = None
    if picture_tag:
        img_tag = picture_tag.find('img')
        if img_tag and 'src' in img_tag.attrs:
            img_url = img_tag['src']

    return {
        "title": title,
        "headline": headline,
        "timestamp": timestamp,
        "crypto_counts": crypto_counts,
        "image_url": img_url,
        "source_url": url  # Add source URL here
    }



# Main function
# Function to get article links from multiple pages
def get_all_article_links(base_url, start_page, end_page):
    all_links = []
    for page in range(start_page, end_page + 1):
        print(f"Fetching articles from page {page}...")
        page_url = f"{base_url}?page={page}"
        links = get_article_links(page_url)
        if links:
            all_links.extend(links)
        time.sleep(1)  # Pause between requests to avoid being blocked
    return all_links

def main():
    # Define the pagination range
    start_page = 1
    end_page = 20

    # Fetch article links across all pages
    article_links = get_all_article_links(base_url, start_page, end_page)
    if not article_links:
        print("No article links found.")
        return

    print(f"Found {len(article_links)} articles. Starting analysis...")

    all_articles_data = []
    for link in article_links:
        print(f"Analyzing article: {link}")
        article_data = analyze_article(link)
        if article_data and article_data['crypto_counts']:
            all_articles_data.append(article_data)
        time.sleep(1)  # Pause between requests

    # Save the results to a JSON file
    with open("crypto_articles_analysis.json", "w") as f:
        json.dump(all_articles_data, f, indent=4)

    print("\nData saved to 'crypto_articles_analysis.json'")


if __name__ == "__main__":
    main()

