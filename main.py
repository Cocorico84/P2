import requests
from bs4 import BeautifulSoup

url = "http://books.toscrape.com/"

# response = requests.get(url)
# soup = BeautifulSoup(response.text, 'html.parser')

# raw_links = soup.findAll('h3')
# links = [i.contents[0]['href'] for i in raw_links]

# next_page = url + soup.findAll(attrs={"class": 'next'})[0].contents[0]['href']

links = []
for n in range(1, 51):
    next_page = f'http://books.toscrape.com/catalogue/page-{n}.html'
    response = requests.get(next_page)
    soup = BeautifulSoup(response.text, 'html.parser')
    raw_links = soup.findAll('h3')
    for i in raw_links:
        links.append(i.contents[0]['href'])


print(len(links))



