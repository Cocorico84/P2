import os
import re

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

URL = "http://books.toscrape.com/"


def get_soup(url: str) -> BeautifulSoup:
    """
    A general function to get a HTML document with data you want to parse

    :param url: URL you want to parse
    :return: a HTML document that you can find elements by tags
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup


def get_all_links_by_category(soup: BeautifulSoup) -> list:
    """
    Give the soup containing all category links

    :param soup: soup from get_soup method
    :type soup: BeautifulSoup type
    :return: a list with all category links
    """
    categories = soup.findAll("a")

    category_links = []
    for i in categories:
        if 'category' in i.get('href'):
            category_links.append(i.get('href'))
    return category_links


def get_all_books_from_category(category_url: str) -> list:
    """
    Give all urls of books from a category

    :param category_url: url of the category
    :return: a list with all book links from a category
    """
    links = []
    for i in get_soup(URL + category_url).findAll('h3'):
        links.append(URL + "catalogue/" + i.contents[0]['href'][9:])
    page = 2
    while True:
        url = URL + category_url.replace('/index.html', f'/page-{page}.html')
        if requests.get(url).status_code == 200:
            book_links = get_soup(url).findAll('h3')
            for i in book_links:
                link = URL + "catalogue/" + i.contents[0]['href'][9:]
                links.append(link)
            page += 1
        else:
            break
    return links


def get_data_from_book(book_urls: list) -> pd.DataFrame:
    """
    Parse each url book to get data and put it into a dictionary then into a dataframe

    :param book_urls: list containing all book urls
    :return: a dataframe with headers from keys and values for each book from a chosen category
    """
    all_data_from_from_from_category = []
    pattern = re.compile("category")
    for url in book_urls:
        soup = get_soup(url)
        keys = [i.contents[0] for i in soup.findAll('th')]
        values = [i.contents[0] for i in soup.findAll('td')]
        data = dict(zip(keys, values))
        title = str(soup.find('h1').contents[0]).replace('/', ' ')
        data['Title'] = title
        category = soup.find_all(href=pattern)[1].contents[0]
        data['Category'] = category
        image_link = "http://books.toscrape.com/" + soup.find('img')['src'][6:]
        data['Image src'] = image_link
        response = requests.get(image_link)
        os.makedirs(f"data/{category}/{category}_images", exist_ok=True)
        with open(f"data/{category}/{category}_images/{title}.jpg", "wb") as file:
            file.write(response.content)
        data['Description'] = soup.select('article > p')[0].contents[0]
        data['Product page url'] = url
        all_data_from_from_from_category.append(data)
    return pd.DataFrame(all_data_from_from_from_category)


def create_csv(csv_name: str, book_urls: list) -> None:
    """
    Transform yor dataframe into a csv

    :param csv_name: the name that you want to give for your csv file
    :param book_urls:
    """
    pd.DataFrame.to_csv(get_data_from_book(book_urls), f'{csv_name}.csv')


if __name__ == '__main__':
    categories = get_all_links_by_category(get_soup(URL))[1:]
    pattern = re.compile(r"books/(.*)_\d+/")
    cat = [re.findall(pattern, i)[0] for i in categories]
    categories_dict = {}
    for i, j in enumerate(cat):
        categories_dict[i] = j
        print(i, j)
    print(50, "all", sep=" ")
    choice = int(input("What category do you want ? (choose a number) : "))
    if 0 <= choice <= 49:
        category_book_links = get_all_books_from_category(categories[choice])
        create_csv(f'data/{categories_dict[choice].capitalize()}/{categories_dict[choice]}_csv', category_book_links)
    elif choice == 50:
        for k, v in tqdm(categories_dict.items()):
            category_book_links = get_all_books_from_category(categories[k])
            create_csv(f'data/{v.capitalize()}/{v}_csv', category_book_links)
    else:
        print("Wrong number")
