import string
import re
import os
import time
from bs4 import BeautifulSoup as bs
import numpy as np
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


def property_to_attr_dict(bs_ele_property):
    """
    getting bs element of single property and returns
    attributes dictionary of the property"""
    proper = bs_ele_property.div.div.findChildren('div', recursive=False)

    try:
        price = proper[0].findChildren('span', recursive=False)[-1].text
        price = ''.join(re.findall("\d", price)).strip()
    except:
        price = None

    attr = proper[1].findChildren('div', recursive=False)

    try:
        type_ = attr[1].text.strip(string.punctuation)
    except:
        type_ = None

    try:
        street = attr[2].findChildren('div', recursive=False)[-2].text.strip(string.punctuation)
    except:
        street = None

    try:
        city = attr[2].findChildren('div', recursive=False)[-1].text.strip(string.punctuation)
    except:
        city = None

    try:
        rooms = attr[3].find('i', {'title': 'Rooms'}).parent.text.strip()
    except:
        rooms = None

    try:
        floor = attr[3].find('i', {'title': 'Floor'}).parent.text.strip()
    except:
        floor = None

    try:
        floor_area = attr[3].find('i', {'title': 'Floor area in sqm'}).parent.text.strip()
    except:
        floor_area = None

    try:
        parking = attr[3].find('i', {'title': 'Parking'}).parent.text.strip()
    except:
        parking = 0

    return {'Price[NIS]': price, 'Property_type': type_, 'City': city, 'Address': street, 'Rooms': rooms,
            'Floor': floor,
            'Area[m^2]': floor_area, 'Parking_spots': parking}


def new_home_to_attr_dict(buy_property):
    proper = buy_property.div.div.findChildren('div', recursive=False)

    try:
        price = proper[0].findChildren('div', recursive=False)[-1].text
        price = ''.join(re.findall("\d", price)).strip()
    except:
        price = None

    attr = proper[1].findChildren('div', recursive=False)

    try:
        Status = attr[-1].text.strip().split()[-1]
    except:
        Status = None

    try:
        street = attr[-3].text.strip(string.punctuation)
    except:
        street = None

    try:
        city = attr[-2].text.strip(string.punctuation)
    except:
        city = None

    return {'Price[NIS]': price, 'Status': Status, 'City': city, 'Address': street}


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
        time.sleep(cfg.SCROLL_PAUSE_TIME)
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

    def _scroll_new_homes(self, verbose=False):
        """
        Scrolls down the new_homes url to load all the information available
        """
        scroll_num = 1
        prev_len = len(self.driver.find_elements_by_xpath(cfg.PROPERTIES_XPATH))
        # maximizing the window makes fewer scrolls necessary
        self.driver.set_window_size(cfg.CHROME_WIDTH, cfg.CHROME_HEIGHT)
        time.sleep(cfg.SCROLL_PAUSE_TIME)
        while True:
            ele_to_scroll = self.driver.find_elements_by_xpath(cfg.PROPERTIES_XPATH)[
                cfg.ELEM_TO_SCROLL_IDX]
            self.driver.execute_script(cfg.SCROLL_COMMAND, ele_to_scroll)
            print_scroll_num(scroll_num, verbose)
            time.sleep(cfg.SCROLL_PAUSE_TIME)
            new_len = len(self.driver.find_elements_by_xpath(cfg.PROPERTIES_XPATH))
            if new_len == prev_len:
                break
            scroll_num += 1
            prev_len = new_len

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

    def _print_save_df(self, df, url, to_print=True, save=False, verbose=False):
        """
        Given a df containing scraped information,
        print it and/or save it to a csv, depending on the user's choice.
        """
        self.update_df(df)
        if 'project' not in url:
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

        if 'project' not in url:
            self._scroll(verbose=kwargs['verbose'])
        else:
            self._scroll_new_homes(verbose=kwargs['verbose'])

        print_scraping(url, verbose=kwargs['verbose'])
        html_doc = self.driver.page_source
        soup = bs(html_doc, 'html.parser')
        content = soup.find('div', {'id': 'propertiesList'}).findChildren("div", recursive=False)
        properties_list = content[1].findChildren('div', recursive=False)
        rows_list = []
        if 'project' not in url:  # for buy, rent and commercial categories
            for proper in properties_list:
                if len(proper.div.div.findChildren('div', recursive=False)) == 2:
                    rows_list.append(property_to_attr_dict(proper))
            df = pd.DataFrame(rows_list)
            df['Price[NIS]'] = df['Price[NIS]'].astype(np.int64)
            df['Rooms'] = df['Rooms'].astype('float')
            df['Floor'] = df['Floor'].astype('float')
            df['Area[m^2]'] = df['Area[m^2]'].astype(np.int64)
            df['Parking_spots'] = df['Parking_spots'].astype(np.int64)
        else:   # for new home category
            for proper in properties_list:
                if len(proper.div.div.findChildren('div', recursive=False)) == 2:
                    rows_list.append(new_home_to_attr_dict(proper))
            df = pd.DataFrame(rows_list)
            df['Price[NIS]'] = df['Price[NIS]'].astype(np.int64)

        self._print_save_df(df, url, to_print=kwargs['to_print'], save=kwargs['save'], verbose=kwargs['verbose'])