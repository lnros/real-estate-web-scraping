import argparse
import os
import time

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager

from config import *
from utils import *


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
        ele_to_scroll = driver.find_elements_by_xpath(PROPERTIES_XPATH)[ELEM_TO_SCROLL_IDX]
        driver.execute_script(SCROLL_COMMAND, ele_to_scroll)
        print_scroll_num(scroll_num, verbose)
        time.sleep(SCROLL_PAUSE_TIME)
        try:
            # Finds the bottom of the page
            bot_ele = driver.find_element_by_xpath(BOTTOM_PAGE_XPATH)
        except NoSuchElementException:
            scroll_num += 1
        except StaleElementReferenceException:
            print("Scrolling forced to end due to unknown error")
            break
        else:
            time.sleep(SCROLL_PAUSE_TIME)
            driver.execute_script(SCROLL_COMMAND, bot_ele)
            break


def save_to_csv(df, url, save=True, verbose=True):
    if save:
        if 'commercial' in url:
            filename = "commercial.csv"
        elif 'projects' in url:
            filename = "new_homes.csv"
        else:
            filename = f"{url.split(URL_SPLIT_SEPARATOR)[FILENAME_IDX]}.csv"
        if verbose:
            print(f'\nSaving {filename}\n')
            print(df)
        df.to_csv(filename)


def print_save_df(zipped, url, to_print, verbose, save):
    """
    Given a zipped file containing scraped information,
    print it and/or save it to a csv, depending on the user's choice.
    """
    df = pd.DataFrame(zipped, columns=COLUMNS)
    print_row(df, to_print=to_print)
    print_total_items(df, verbose=verbose)
    save_to_csv(df, url, save=save, verbose=verbose)


def scrap_url(driver, url, to_print=True, save=False, verbose=False):
    """
    Scraps properties' information given the url and either prints it to the screen and/or save it to a csv file
    """

    print_access(url, verbose)
    driver.get(url)
    print_scrolling(url, verbose)
    scroll(driver=driver, verbose=verbose)
    print_scraping(url, verbose)
    # TODO handle new homes inside buy, because it causes asymmetry when zipping
    prices = (price.text.split()[PRICE_IDX] for price in
              driver.find_elements_by_xpath(PRICE_XPATH))
    prop_types = (prop_type.text.split('\n')[PROPERTY_TYPE_IDX] for prop_type in
                  driver.find_elements_by_xpath(PROP_TYPE_XPATH))
    cities = (address.text.split('\n')[CITY_IDX] for address in
              driver.find_elements_by_xpath(CITY_XPATH))
    addresses = (address.text.split('\n')[ADDRESS_IDX] for address in
                 driver.find_elements_by_xpath(ADDRESS_XPATH))
    nums_rooms = (num_rooms.text.split()[NUM_OF_ROOMS_IDX]
                  if (len(num_rooms.text.split()) != SINGLE_ATR_ITEM) else TRIVIAL_NUMBER
                  for num_rooms in driver.find_elements_by_xpath(NUM_ROOMS_XPATH))
    floors = (floor.text.split()[FLOOR_IDX]
              if len(floor.text.split()) > FLOOR_IDX and len(floor.text.split()) > INVALID_FLOOR_TEXT_SIZE
              else TRIVIAL_NUMBER for floor in driver.find_elements_by_xpath(FLOOR_XPATH))
    sizes = (size.text.split()[SIZE_IDX] if (len(size.text.split()) > SIZE_IDX)
             else size.text.split()[SIZE_TEXT_IDX] if (len(size.text.split()) == SINGLE_ATR_ITEM) else TRIVIAL_NUMBER
             for size in driver.find_elements_by_xpath(SIZE_XPATH))
    parking_spaces = (parking.text.split()[PARKING_SPACES_IDX] if len(parking.text.split()) > PARKING_SPACES_IDX
                      else TRIVIAL_NUMBER
                      for parking in driver.find_elements_by_xpath(PARKING_XPATH))
    zipped = zip(prices, prop_types, cities, addresses, nums_rooms, floors, sizes, parking_spaces)
    print_save_df(zipped, to_print=to_print, save=save, verbose=verbose)


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
    configs = Configuration(property_listing_type=args.property_listing_type,
                            to_print=args.print,
                            save=args.save,
                            verbose=args.verbose)
    urls = [URLS[key] for key in listing_type[configs.property_listing_type]]

    driver = create_driver()

    for url in urls:
        scrap_url(driver, url, to_print=configs.to_print, save=configs.save, verbose=configs.verbose)
        driver.close()
    driver.quit()
    print_when_program_finishes()


if __name__ == '__main__':
    main()
