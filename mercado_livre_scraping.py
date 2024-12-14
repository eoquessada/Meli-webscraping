from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
from pathlib import Path
from datetime import datetime

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
        html_tags = soup.find_all('a', class_='poly-component__title')
        return [tag.get_text(strip=True) for tag in html_tags]
    else:
        return []


def get_items_prices(soup):
    """Extract and return the current prices of promotion items from the BeautifulSoup object."""
    if soup:
        prices = []
        # Encontre todas as divs com o preço atual
        current_price_divs = soup.find_all('div', class_='poly-price__current')
        for div in current_price_divs:
            # Dentro de cada div, pegue os reais e centavos
            reais = div.find('span', class_='andes-money-amount__fraction')
            centavos = div.find('span', class_='andes-money-amount__cents')
            # Combine reais e centavos (ou "00" se centavos não existirem)
            reais_text = reais.get_text(strip=True) if reais else "0"
            centavos_text = centavos.get_text(strip=True) if centavos else "00"
            prices.append(f"R$ {reais_text},{centavos_text}")
        return prices
    else:
        return []




def get_items_discounts(soup):
    """Extract and return the discount of promotion items from the BeautifulSoup object."""
    if soup:
        html_tags = soup.find_all('span', class_='andes-money-amount__discount')
        return [tag.get_text(strip=True) for tag in html_tags]
    else:
        return []


def get_timestamp(df, column):
    timestamp = datetime.now()
    df[column] = timestamp
    return df

def scrap_all_pages(base_url, max_pages, column_names):
    """Scrap all pages from offer products"""
    all_products_titles = []
    all_products_prices = []
    all_products_discounts = []
    for i in range(max_pages):
        page_url = f"{base_url}{i+1}"
        response_text = get_response_text(page_url)
        soup = beautify_text(response_text)
        titles = get_items_title(soup)
        prices = get_items_prices(soup)
        discounts = get_items_discounts(soup)
        if titles:
            all_products_titles.extend(titles)
            all_products_prices.extend(prices)
            all_products_discounts.extend(discounts)
        else:
            break  
    all_products = zip(all_products_titles, all_products_prices, all_products_discounts)
    promotion_products = pd.DataFrame(all_products, columns=column_names)
    promotion_products_final = get_timestamp(promotion_products, 'included_in')
    return promotion_products_final

def dataframe_to_csv(dataframe):
    """Convert dataframe to csv and export do Downloads folder"""
    user_home = Path.home()
    downloads_folder = user_home/"Downloads"
    file_path = downloads_folder/"meli_offers_dataframe.csv"
    dataframe.to_csv(file_path, index = None, header=True) 
    return None


url = 'https://www.mercadolivre.com.br/ofertas?container_id=MLB779362-1&page='
max_pages = 20
offers = scrap_all_pages(url, max_pages, ['Product', 'Price', 'Discount'])
dataframe_to_csv(offers)
print(offers)