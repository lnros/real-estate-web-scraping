import os
import requests
from bs4 import BeautifulSoup as bs


def get_html_to_txt(urls, destination='txt_files'):
    """
    TODO Docstrings
    """
    assert isinstance(urls, dict)
    assert isinstance(destination, str)

    for name, url in urls.items():
        content = requests.get(url)
        content.encoding = 'ISO-8859-1'
        try:
            file = open(f'{destination}/{name}.html', 'w')
        except FileNotFoundError:
            os.mkdir(f'{destination}')
            file = open(f'{destination}/{name}.html', 'w')
        finally:
            file.write(str(content.text))
            file.close()

def parser(filepath):
    """
    TODO Docstrings
    """
    try:
        with open(filepath) as file:
            soup = bs(file, 'lxml')
        match = soup.title.text
        return match
    except FileNotFoundError as error:
        raise error

def main():
    """
    TODO Docstrings
    """
    urls = {
        'buy': 'http://www.immobilier.co.il/recherche.php?currency=1&tip%5B%5D=0&tip%5B%5D=2&region=-1&Submit=Rechercher&bienra=',
        'rent': 'http://www.immobilier.co.il/recherche.php?currency=1&tip%5B%5D=1&tip%5B%5D=3&region=-1&Submit=Rechercher&bienra=',
        'new': 'http://www.immobilier.co.il/recherche.php?currency=1&tip%5B%5D=2&region=-1&Submit=Rechercher&bienra='
    }
    html_path = 'html_files'
    get_html_to_txt(urls, html_path)
    # files = os.scandir(txt_path)
    for file in os.scandir(html_path):
        print(parser(file))



if __name__ == '__main__':
    main()