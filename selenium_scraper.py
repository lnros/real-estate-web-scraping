import os
import time

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

from config import Configuration as cfg
from utils import *


def create_driver():
    """
    Creates a driver that runs in Google Chrome.
    """
    os.environ['WDM_LOG_LEVEL'] = cfg.SILENCE_DRIVER_LOG
    return webdriver.Chrome(ChromeDriverManager().install())


class SeleniumScraper:

    def __init__(self):
        self.driver = create_driver()
        self._df = None

    def update_df(self, df):
        """
        Updates the dataframe containing the scraped info
        """
        self._df = df

    def get_df(self):
        """
        Returns the dataframe containing the scraped info
        """
        return self._df

    def _scroll(self, verbose=False):
        """
        Scrolls down the url to load all the information available
        """
        scroll_num = 1
        # maximizing the window makes fewer scrolls necessary
        self.driver.set_window_size(cfg.CHROME_WIDTH, cfg.CHROME_HEIGHT)
        while True:
            ele_to_scroll = self.driver.find_elements_by_xpath(cfg.PROPERTIES_XPATH)[
                cfg.ELEM_TO_SCROLL_IDX]
            self.driver.execute_script(cfg.SCROLL_COMMAND, ele_to_scroll)
            print_scroll_num(scroll_num, verbose)
            time.sleep(cfg.SCROLL_PAUSE_TIME)
            try:
                # Finds the bottom of the page
                bot_ele = self.driver.find_element_by_xpath(cfg.BOTTOM_PAGE_XPATH)
            except NoSuchElementException:
                scroll_num += 1
            else:
                time.sleep(cfg.SCROLL_PAUSE_TIME)
                self.driver.execute_script(cfg.SCROLL_COMMAND, bot_ele)
                break

    def _save_to_csv(self, url, save=True, verbose=True):
        """
        Save the dataframe containing the scraped info into a csv file
        """
        if save:
            if 'commercial' in url:
                filename = "commercial.csv"
            elif 'projects' in url:
                filename = "new_homes.csv"
            else:
                filename = f"{url.split(cfg.URL_SPLIT_SEPARATOR)[cfg.FILENAME_IDX]}.csv"
            if verbose:
                print(f'\nSaving {filename}\n')
                print(self.get_df())
            self.get_df().to_csv(filename)

    def _print_save_df(self, zipped, url, to_print=True, save=False, verbose=False):
        """
        Given a zipped file containing scraped information,
        print it and/or save it to a csv, depending on the user's choice.
        """
        self.update_df(pd.DataFrame(zipped, columns=cfg.COLUMNS))
        print_row(self.get_df(), to_print=to_print)
        print_total_items(self.get_df(), verbose=verbose)
        self._save_to_csv(url, save=save, verbose=verbose)

    def scrap_url(self, url, **kwargs):
        """
        Scrapes properties' information given the url and either prints it to the screen and/or save it to a csv file
        ----
        Options available with kwargs:
        to_print: bool
        save: bool
        verbose: bool
        """

        print_access(url, verbose=kwargs['verbose'])
        self.driver.get(url)
        print_scrolling(url, verbose=kwargs['verbose'])
        self._scroll(verbose=kwargs['verbose'])
        print_scraping(url, verbose=kwargs['verbose'])
        # TODO handle new homes inside buy, because it causes asymmetry when zipping
        prices = (price.text.split()[cfg.PRICE_IDX] for price in self.driver.find_elements_by_xpath(cfg.PRICE_XPATH))
        prop_types = (prop_type.text.split('\n')[cfg.PROPERTY_TYPE_IDX] for prop_type in
                      self.driver.find_elements_by_xpath(cfg.PROP_TYPE_XPATH))
        cities = (address.text.split('\n')[cfg.CITY_IDX] for address in
                  self.driver.find_elements_by_xpath(cfg.CITY_XPATH))
        addresses = (address.text.split('\n')[cfg.ADDRESS_IDX] for address in
                     self.driver.find_elements_by_xpath(cfg.ADDRESS_XPATH))
        nums_rooms = (num_rooms.text.split()[cfg.NUM_OF_ROOMS_IDX]
                      if (len(num_rooms.text.split()) != cfg.SINGLE_ATR_ITEM) else cfg.TRIVIAL_NUMBER
                      for num_rooms in self.driver.find_elements_by_xpath(cfg.NUM_ROOMS_XPATH))
        floors = (floor.text.split()[cfg.FLOOR_IDX] if len(floor.text.split()) > cfg.FLOOR_IDX and len(
            floor.text.split()) > cfg.INVALID_FLOOR_TEXT_SIZE else cfg.TRIVIAL_NUMBER for floor in
                  self.driver.find_elements_by_xpath(cfg.FLOOR_XPATH))
        sizes = (size.text.split()[cfg.SIZE_IDX] if (len(size.text.split()) > cfg.SIZE_IDX)
                 else size.text.split()[cfg.SIZE_TEXT_IDX] if (
                len(size.text.split()) == cfg.SINGLE_ATR_ITEM) else cfg.TRIVIAL_NUMBER
                 for size in self.driver.find_elements_by_xpath(cfg.SIZE_XPATH))
        parking_spaces = (parking.text.split()[cfg.PARKING_SPACES_IDX]
                          if len(parking.text.split()) > cfg.PARKING_SPACES_IDX else cfg.TRIVIAL_NUMBER
                          for parking in self.driver.find_elements_by_xpath(cfg.PARKING_XPATH))
        zipped = zip(prices, prop_types, cities, addresses, nums_rooms, floors, sizes, parking_spaces)
        self._print_save_df(zipped, url, to_print=kwargs['to_print'], save=kwargs['save'], verbose=kwargs['verbose'])
