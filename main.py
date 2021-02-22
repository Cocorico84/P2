import requests
from bs4 import BeautifulSoup
import pandas as pd
import re


def get_soup(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup


def get_all_links_by_category(soup):
    categories = soup.findAll("a")

    category_links = []
    for i in categories:
        if 'category' in i.get('href'):
            category_links.append(i.get('href'))
    return category_links


def get_all_books_from_category(category_url):
    links = []
    for i in get_soup("http://books.toscrape.com/" + category_url).findAll('h3'):
        links.append("http://books.toscrape.com/catalogue/" + i.contents[0]['href'][9:])
    page = 2
    while True:
        url = "http://books.toscrape.com/" + category_url.replace('/index.html', f'/page-{page}.html')
        if requests.get(url).status_code == 200:
            book_links = get_soup(url).findAll('h3')
            for i in book_links:
                link = "http://books.toscrape.com/catalogue/" + i.contents[0]['href'][9:]
                links.append(link)
            page += 1
        else:
            break
    return links


def get_data_from_book(book_urls):
    all_data_from_from_from_category = []
    for url in book_urls:
        keys = [i.contents[0] for i in get_soup(url).findAll('th')]
        values = [i.contents[0] for i in get_soup(url).findAll('td')]
        data = dict(zip(keys, values))
        data['Title'] = get_soup(url).find('h1').contents[0]
        data['Category'] = get_soup(url).find_all(href=re.compile("category"))[1].contents[0]
        data['Image src'] = "http://books.toscrape.com/" + get_soup(url).find('img')['src'][6:]
        data['Description'] = get_soup(url).select('article > p')[0].contents[0]
        data['Product page url'] = url
        all_data_from_from_from_category.append(data)
    return pd.DataFrame(all_data_from_from_from_category)


def create_csv(csv_name, book_urls):
    pd.DataFrame.to_csv(get_data_from_book(book_urls), f'{csv_name}.csv')


if __name__ == '__main__':
    url = "http://books.toscrape.com/"
    categories = get_all_links_by_category(get_soup(url))[1:]
    cat = [re.findall(r"books/(?P<cat>.*)_\d+/", i)[0] for i in categories]
    categories_dict = {}
    for i,j in enumerate(cat):
        categories_dict[i] = j
        print(i,j)
    choice = int(input("What category do you want ? : "))
    category_book_links = get_all_books_from_category(categories[choice])
    create_csv(f'{categories_dict[choice]}_csv', category_book_links)
