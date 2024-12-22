import requests
import os
import bs4
import pandas as pd
import random
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create 'assets' directory if it doesn't exist
if not os.path.exists('assets'):
    os.makedirs('assets')

database = {"title": [], "price": [], "discount": [], "link": []}
query = 'GB'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0 Safari/537.36'
}

# Retrieve proxy credentials from environment variables
proxy_username = os.getenv('PROXY_USERNAME')
proxy_password = os.getenv('PROXY_PASSWORD')

proxy_list = [
    f"http://{proxy_username}:{proxy_password}@198.23.239.134:6540",
    f"http://{proxy_username}:{proxy_password}@207.244.217.165:6712",
    f"http://{proxy_username}:{proxy_password}@107.172.163.27:6543",
    f"http://{proxy_username}:{proxy_password}@64.137.42.112:5157",
    f"http://{proxy_username}:{proxy_password}@173.211.0.148:6641",
    f"http://{proxy_username}:{proxy_password}@161.123.152.115:6360",
    f"http://{proxy_username}:{proxy_password}@167.160.180.203:6754",
    f"http://{proxy_username}:{proxy_password}@154.36.110.199:6853",
    f"http://{proxy_username}:{proxy_password}@173.0.9.70:5653",
    f"http://{proxy_username}:{proxy_password}@173.0.9.209:5792"
]

for i in range(1, 3):
    print(f"Fetching page {i}...")
    proxy = random.choice(proxy_list)
    proxies = {
        "http": proxy,
        "https": proxy
    }
    try:
        page = requests.get(f'https://www.offertag.in/deals/search?deals=3&q={query}&page={i}', headers=headers, proxies=proxies)
        page.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching page {i} with proxy {proxy}: {e}")
        continue

    try:
        with open(f'offer_page{i}.html', 'w') as f:
            f.write(page.text)
    except IOError as e:
        print(f"Error writing to file offer_page{i}.html: {e}")
        continue

    soup = bs4.BeautifulSoup(page.content, 'html.parser')
    for i in soup.find_all('div', class_='featured-item-container'):
        try:
            image = i.find('img')['data-src']
            title = i.find('h4').text
            valid_title = "".join(x for x in title if x.isalnum() or x in "._- ")
            valid_title = valid_title[1:-7]
            price = i.find('div', class_='new-price').text
            discount = i.find('div', class_='discount').text
            link = f"https://www.offertag.in" + i.find('a')['href']
            database['title'].append(valid_title)
            database['price'].append(price[2:-1])
            database['link'].append(link)
            database['discount'].append(discount)
            
            cover = requests.get(image, headers=headers)
            cover.raise_for_status()
            with open(f'assets/{valid_title}.png', 'wb') as f:
                f.write(cover.content)
        except (requests.RequestException, IOError) as e:
            print(f"Error processing item with proxy {proxy}: {e}")
            continue

try:
    df = pd.DataFrame(data=database)
    df.to_csv('offers.csv', index=False, encoding='utf-8')
except IOError as e:
    print(f"Error writing to CSV file: {e}")