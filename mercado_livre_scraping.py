from bs4 import BeautifulSoup
import requests
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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

def get_items_prices(soup):
    """Extract and return the prices of promotion items from the BeautifulSoup object."""
    if soup:
        html_tags = soup.find_all('span', class_='andes-money-amount andes-money-amount--cents-superscript')
        return [tag['aria-label'] for tag in html_tags]
    else:
        return []

# TODO: Tranfsorm price data (create a func)
def scrap_all_pages(base_url, max_pages, column_names):
    """Scrap all pages from offer products"""
    all_products_titles = []
    all_products_prices = []
    for i in range(max_pages):
        page_url = f"{base_url}{i+1}"
        response_text = get_response_text(page_url)
        soup = beautify_text(response_text)
        titles = get_items_title(soup)
        prices = get_items_prices(soup)
        if titles:
            all_products_titles.extend(titles)
            all_products_prices.extend(prices)
        else:
            break  
    all_products = zip(all_products_titles, all_products_prices)
    return pd.DataFrame(all_products, columns=column_names)

# TODO: Refactor func send_email (email_password should not be passed as an argument of send_email)
def send_email(email_from, email_to, dataframe, email_password):
    msg = MIMEMultipart()
    msg['From'] = email_from
    msg['To'] = email_to
    msg['Subject'] = "Novas Ofertas Mercado Livre!"

    body = f"<p>Novas Ofertas do Mercado Livre para você!</p><p>{dataframe.to_html()}</p>"
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        # Use your App Password instead of your regular password
        server.login(email_from, email_password)
        server.sendmail(msg['From'], [msg['To']], msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")


url = 'https://www.mercadolivre.com.br/ofertas?container_id=MLB779362-1&page='
max_pages = 20
offers = scrap_all_pages(url, max_pages, ['products', 'prices'])
send_email('joaoquessada4@gmail.com', 'joaoquessada4@gmail.com', offers, 'mysecretpassword')
print(offers)