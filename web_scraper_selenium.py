import argparse
import os
import time
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

PROPERTY_LISTING_TYPE = ('buy', 'rent', 'commercial', 'new homes', 'all')
MAIN_URL = 'https://www.onmap.co.il/en'
# TODO implement commercial and new homes (their html is different)
URLS = {'buy': MAIN_URL + '/homes/buy',
        'rent': MAIN_URL + '/homes/rent',
        'commercial': MAIN_URL + '/commercial/rent/',
        'new homes': MAIN_URL + '/projects/'}
PROPERTY_TYPE_IDX = 1
NUM_OF_ROOMS_IDX = 0
FLOOR_IDX = 1
SIZE_IDX = 2
PARKING_SPACES_IDX = 3
SCROLL_PAUSE_TIME = 2
COLUMNS = ['Price[NIS]','Property_type', 'Address', 'Rooms', 'Floor', 'Area[m^2]', 'Parking_spots']


def define_parser():
    """
    Creates the command line arguments
    """
    arg_parser = argparse.ArgumentParser(description="Scraping OnMap website | Checkout https://www.onmap.co.il/en/")
    arg_parser.add_argument(
        "property_listing_type",
        choices=PROPERTY_LISTING_TYPE,
        help="'buy' or 'rent' or 'all'",
        type=str)
    arg_parser.add_argument("--print", '-p', help="print the results to the screen", action="store_true")
    arg_parser.add_argument("--save", '-s', help="save the scraped information into a csv file in the same directory",
                            action="store_true")
    arg_parser.add_argument("--verbose", '-v', help="prints messages during the scraper execution", action="store_true")
    return arg_parser.parse_args()


def create_driver():
    """
    Creates a driver that runs in Google Chrome without the user seeing an open browser window
    """
    # silent web_driver log
    os.environ['WDM_LOG_LEVEL'] = '0'
    opts = webdriver.ChromeOptions()
    opts.headless = True
    return webdriver.Chrome(ChromeDriverManager().install(), options=opts)


def scroll(driver, verbose=False):
    """
    Scrolls down the url to load all the information available
    """
    scroll_num = 1
    while True:
        ele_to_scroll = driver.find_elements_by_xpath("//*[@id='propertiesList']/div[2]/div")[-1]
        driver.execute_script("arguments[0].scrollIntoView();", ele_to_scroll)
        if verbose:
            print(f"Scroll nº {scroll_num}")
        time.sleep(SCROLL_PAUSE_TIME)
        try:
            # Finds the bottom
            driver.find_element_by_xpath("//div[@class='G3BoaHW05R4rguvqgn-Oo']")
        except NoSuchElementException:
            scroll_num += 1
        else:
            break



def scrap_url(driver, url, to_print=True, save=False, verbose=False):
    """
    Scraps properties' information given the url and either prints it to the screen and/or save it to a csv file
    """
    if verbose:
        print(f'Accessing {url}')
    driver.get(url)
    if verbose:
        print(f"Scrolling down {url}")
    scroll(driver, verbose=verbose)
    if verbose:
        print(f"Scraping {url}")
    prices = (price.text for price in driver.find_elements_by_xpath("//span[@class='cWr2cxa0k3zKePxbqpw3L']"))
    prop_types = (prop_type.text.split('\n')[PROPERTY_TYPE_IDX] for prop_type in
                  driver.find_elements_by_xpath("//div[@class='_1bluUEiq7lEDSV1yeF9mjl']"))
    addresses = (address.text for address in driver.find_elements_by_xpath("//div[@property='address']"))
    nums_rooms = (num_rooms.text.split()[NUM_OF_ROOMS_IDX] for num_rooms in
                  driver.find_elements_by_xpath("//div[@class='yHLZr2apXqwIyhsOGyagJ']"))
    floors = (floor.text.split()[FLOOR_IDX] for floor in
              driver.find_elements_by_xpath("//div[@class='yHLZr2apXqwIyhsOGyagJ']"))
    sizes = (size.text.split()[SIZE_IDX] for size in
             driver.find_elements_by_xpath("//div[@class='yHLZr2apXqwIyhsOGyagJ']"))
    parking_spaces = (parking.text.split()[PARKING_SPACES_IDX] if len(parking.text.split()) > PARKING_SPACES_IDX else 0
                      for parking in driver.find_elements_by_xpath("//div[@class='yHLZr2apXqwIyhsOGyagJ']"))
    zipped = zip(prices, prop_types, addresses, nums_rooms, floors, sizes, parking_spaces)
    if to_print:
        for price, prop_type, address, num_rooms, floor, size, parking in zipped:
            print(f"Price: {price}, Type: {prop_type}, Address: {address}, "
                  f"Nº Rooms: {num_rooms}, Floor: {floor}, Size {size}, Parking: {parking}")

    if save:
        filename = f"{url.split('/')[-1]}.csv"
        if verbose:
            print(f'Saving {filename}')
        df = pd.DataFrame(zipped, columns=COLUMNS)
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
        'new homes': ['new homes'],
        'all': ['buy', 'rent', 'commercial', 'new homes']
    }

    if args.property_listing_type not in PROPERTY_LISTING_TYPE:
        print(f'You should choose of one the following: {PROPERTY_LISTING_TYPE},'
              f' but you provided {args.property_listing_type}')
        return

    urls = [URLS[key] for key in listing_type[args.property_listing_type]]
    driver = create_driver()
    for url in urls:
        scrap_url(driver, url, to_print=args.print, save=args.save, verbose=args.verbose)
    driver.quit()
    print('Done!')


if __name__ == '__main__':
    main()
