from bs4 import BeautifulSoup
import requests
import pandas as pd

def get_response_text(url):
    """Fetch the content of the given URL and return the response text."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def beautify_text(response_text):
    """Parse the response text with BeautifulSoup and return the BeautifulSoup object."""
    if response_text:
        return BeautifulSoup(response_text, 'html.parser')
    else:
        return None

def get_items_title(soup):
    """Extract and return the titles of promotion items from the BeautifulSoup object."""
    if soup:
        html_tags = soup.find_all('p', class_='promotion-item__title')
        return [tag.get_text(strip=True) for tag in html_tags]
    else:
        return []

def scrap_all_pages(base_url, max_pages, column_name):
    """Scrap all pages from offer products"""
    products = []
    for i in range(max_pages):
        page_url = f"{base_url}{i+1}"
        response_text = get_response_text(page_url)
        soup = beautify_text(response_text)
        titles = get_items_title(soup)
        if titles:
            products.extend(titles)
        else:
            break  # Stop if no titles are found on the page
    return pd.DataFrame(products, columns=[column_name])

url = 'https://www.mercadolivre.com.br/ofertas?container_id=MLB779362-1&page='
max_pages = 20
offers = scrap_all_pages(url, max_pages, 'offers')
print(offers)