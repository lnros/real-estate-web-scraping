import os
import sys

import requests
from bs4 import BeautifulSoup as bs

NUM_ARGS_NO_ARGS = 1
NUM_ARGS_HELP = 2
# urls for this project only
URLS = {
    # 'onmap': 'https://www.onmap.co.il/en/homes/buy/c_31.943030,34.796780/t_32.178710,35.250310/z_10',
    'buy': 'http://www.immobilier.co.il/recherche.php?currency=1&tip%5B%5D=0&tip%5B%5D=2&region=-1&Submit=Rechercher&bienra=',
    'rent': 'http://www.immobilier.co.il/recherche.php?currency=1&tip%5B%5D=1&tip%5B%5D=3&region=-1&Submit=Rechercher&bienra=',
    'new': 'http://www.immobilier.co.il/recherche.php?currency=1&tip%5B%5D=2&region=-1&Submit=Rechercher&bienra='
}

HELP_STRING = "usage: ./web_scraper.py url_name url"  # TODO Help string


def get_html_to_txt(urls, destination='html_files'):
    """
    TODO Docstrings
    """
    assert isinstance(urls, dict)
    assert isinstance(destination, str)

    for name, url in urls.items():
        try:
            content = requests.get(url)
            content.encoding = 'ISO-8859-1'
            file = open(f'{destination}/{name}.html', 'w')
        except requests.exceptions.MissingSchema as error:
            print(error)
        except FileNotFoundError:
            print("Destination directory does not exist.")
        else:
            file.write(str(content.text))
            file.close()


def parser(filepath):
    """
    TODO Docstrings
    """
    try:
        with open(filepath) as file:
            soup = bs(file, 'lxml')
        property_info = soup.find_all('div', class_='property-info')
        return property_info
    except FileNotFoundError as error:
        raise error


def test():
    """
    TODO Docstrings
    """

    html_path = 'html_files'
    get_html_to_txt(URLS, html_path)
    for file in os.scandir(html_path):
        print(parser(file))


def main():
    """
    TODO Docstrings
    """
    # TODO command line interface
    if len(sys.argv) == NUM_ARGS_HELP and sys.argv[1] == '--help':
        print(HELP_STRING)
        return
    elif len(sys.argv) == NUM_ARGS_NO_ARGS:
        print(f'ERROR: No arguments were given.\nFor proper usage:\n{HELP_STRING}', )
        return


if __name__ == '__main__':
    test()
