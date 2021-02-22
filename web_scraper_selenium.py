import argparse
import os
import time
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import string

PRINTABLE = set(string.printable)
SILENCE_DRIVER_LOG = '0'
CHROME_WIDTH = 1919
CHROME_HEIGHT = 1079
PROPERTY_LISTING_TYPE = ('buy', 'rent', 'commercial', 'new_homes', 'all')
MAIN_URL = 'https://www.onmap.co.il/en'
# TODO implement commercial and new homes (their html is different)
URLS = {'buy': MAIN_URL + '/homes/buy',
        'rent': MAIN_URL + '/homes/rent',
        'commercial': MAIN_URL + '/commercial/rent/',
        'new homes': MAIN_URL + '/projects/'}
PRICE_IDX = -1
CITY_IDX = -1
ADDRESS_IDX = -2
PROPERTY_TYPE_IDX = 1
NUM_OF_ROOMS_IDX = 0
FLOOR_IDX = 1
SIZE_IDX = 2
PARKING_SPACES_IDX = 3
SCROLL_PAUSE_TIME = 1
COLUMNS = ['Price[NIS]', 'Property_type', 'City', 'Address', 'Rooms', 'Floor', 'Area[m^2]', 'Parking_spots']


def define_parser():
    """
    Creates the command line arguments
    """
    arg_parser = argparse.ArgumentParser(description="Scraping OnMap website | Checkout https://www.onmap.co.il/en/")
    arg_parser.add_argument(
        "property_listing_type",
        choices=PROPERTY_LISTING_TYPE,
        help="choose which type of properties you would like to scrape",
        type=str)
    arg_parser.add_argument("--print", '-p', help="print the results to the screen", action="store_true")
    arg_parser.add_argument("--save", '-s', help="save the scraped information into a csv file in the same directory",
                            action="store_true")
    arg_parser.add_argument("--verbose", '-v', help="prints messages during the scraper execution", action="store_true")
    return arg_parser.parse_args()


def create_driver():
    """
    Creates a driver that runs in Google Chrome.
    """
    os.environ['WDM_LOG_LEVEL'] = SILENCE_DRIVER_LOG
    return webdriver.Chrome(ChromeDriverManager().install())


def scroll(driver, verbose=False):
    """
    Scrolls down the url to load all the information available
    """
    scroll_num = 1
    # maximizing the window makes fewer scrolls necessary
    driver.set_window_size(CHROME_WIDTH, CHROME_HEIGHT)
    while True:
        ele_to_scroll = driver.find_elements_by_xpath("//*[@id='propertiesList']/div[2]/div")[-1]
        driver.execute_script("arguments[0].scrollIntoView();", ele_to_scroll)
        if verbose:
            print(f"Scroll nº {scroll_num}")
        time.sleep(SCROLL_PAUSE_TIME)
        try:
            # Finds the bottom of the page
            bot_ele = driver.find_element_by_xpath("//div[@class='G3BoaHW05R4rguvqgn-Oo']")
        except NoSuchElementException:
            scroll_num += 1
        else:
            time.sleep(SCROLL_PAUSE_TIME)
            driver.execute_script("arguments[0].scrollIntoView();", bot_ele)
            break


def scrap_url(driver, url, to_print=True, save=False, verbose=False):
    """
    Scraps properties' information given the url and either prints it to the screen and/or save it to a csv file
    """
    if verbose:
        print(f'\nAccessing {url}\n')
    driver.get(url)
    if verbose:
        print(f"\nScrolling down {url}\n")
    scroll(driver=driver, verbose=verbose)
    if verbose:
        print(f"\nScraping {url}\n")

    prices = (price.text.split()[PRICE_IDX] for price in
              driver.find_elements_by_xpath("//span[@class='cWr2cxa0k3zKePxbqpw3L']"))
    prop_types = (prop_type.text.split('\n')[PROPERTY_TYPE_IDX] for prop_type in
                  driver.find_elements_by_xpath("//div[@class='_1bluUEiq7lEDSV1yeF9mjl']"))
    cities = (address.text.split('\n')[CITY_IDX] for address in
              driver.find_elements_by_xpath("//div[@property='address']"))
    addresses = (address.text.split('\n')[ADDRESS_IDX] for address in
                 driver.find_elements_by_xpath("//div[@property='address']"))
    nums_rooms = (num_rooms.text.split()[NUM_OF_ROOMS_IDX] for num_rooms in
                  driver.find_elements_by_xpath("//div[@class='yHLZr2apXqwIyhsOGyagJ']"))
    floors = (floor.text.split()[FLOOR_IDX] for floor in
              driver.find_elements_by_xpath("//div[@class='yHLZr2apXqwIyhsOGyagJ']"))
    sizes = (size.text.split()[SIZE_IDX] for size in
             driver.find_elements_by_xpath("//div[@class='yHLZr2apXqwIyhsOGyagJ']"))
    parking_spaces = (parking.text.split()[PARKING_SPACES_IDX] if len(parking.text.split()) > PARKING_SPACES_IDX else 0
                      for parking in driver.find_elements_by_xpath("//div[@class='yHLZr2apXqwIyhsOGyagJ']"))
    zipped = zip(prices, prop_types, cities, addresses, nums_rooms, floors, sizes, parking_spaces)
    df = pd.DataFrame(zipped, columns=COLUMNS)

    if to_print:
        for index, row in df.iterrows():
            print(
                f"Price: {row['Price[NIS]']}, Type: {row['Property_type']}, City: {row['City']}, Address: {row['Address']}, "
                f"Nº Rooms: {row['Rooms']}, Floor: {row['Floor']}, Size {row['Area[m^2]']}, Parking: {row['Parking_spots']}")

    if verbose:
        num_items = len(df)
        print(f'\nScraped total of {num_items} items\n')

    if save:
        filename = f"{url.split('/')[-1]}.csv"
        if verbose:
            print(f'\nSaving {filename}\n')
            print(df)
        df.to_csv(filename)


def main():
    """
    Prints to the screen or save it to a csv file buy and/or rent real estate scraped data from the OnMap website
    """
    args = define_parser()
    listing_type = {
        'buy': ['buy'],
        'rent': ['rent'],
        'commercial': ['commercial'],
        'new_homes': ['new homes'],
        'all': ['buy', 'rent', 'commercial', 'new homes']
    }

    urls = [URLS[key] for key in listing_type[args.property_listing_type]]

    driver = create_driver()

    for url in urls:
        scrap_url(driver, url, to_print=args.print, save=args.save, verbose=args.verbose)
        driver.close()
    driver.quit()
    print('\nDone!\n')


if __name__ == '__main__':
    main()
