from bs4 import BeautifulSoup
import requests

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

def get_items_price(soup):
    """Extract and return the prices of promotion items from the BeautifulSoup object."""
    if soup:
        prices = []
        html_tags_currency = soup.find_all('span', class_='andes-money-amount__currency-symbol')
        html_tags_price = soup.find_all('span', class_='andes-money-amount__fraction')
        for i in range(len(html_tags_currency)):
            currency = html_tags_currency[i]
            price = html_tags_price[i]
            full_price = f"{currency} {price}"
            prices.append(full_price)
        return prices
    else:
        return []

def get_items_price_description(soup):
    """Extract and return the prices descriptions of promotion items from the BeautifulSoup object."""
    if soup:
        prices_descriptions = []
        html_tags = soup.find_all('span', class_='promotion-item__installments')
        for tag in html_tags:
            main_price = tag.contents[0].strip()
            centavos = tag.find('sup').get_text(strip=True)
            full_price_description = f"{main_price}.{centavos}"
            prices_descriptions.append(full_price_description)
        return prices_descriptions
    else:
        return []
    
def main(url):
    """Main function to fetch and print promotion item titles and prices."""
    response_text = get_response_text(url)
    soup = beautify_text(response_text)
    titles = get_items_title(soup)
    prices = get_items_price_description(soup)
    products = {title: price for title, price in zip(titles, prices)}
    print(products)


if __name__ == "__main__":
    url = 'https://www.mercadolivre.com.br/ofertas'
    main(url)
