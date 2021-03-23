import os
import time

import numpy as np
import pandas as pd
import pymysql
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

from config import Configuration as cfg
from config import DBConfig
from config import Logger as Log
from utils import *
import data_base_feeder
from data_base_feeder import DataBaeFeeder


class SeleniumScraper:

    def __init__(self):
        self.driver = self._create_driver()
        self._df = None

    @staticmethod
    def _create_driver():
        """
        Creates a driver that runs in Google Chrome.
        """
        os.environ['WDM_LOG_LEVEL'] = cfg.SILENCE_DRIVER_LOG
        return webdriver.Chrome(ChromeDriverManager().install())

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

    def _scroll(self, limit=None, verbose=False):
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
            if ele_to_scroll is None:
                Log.logger.error(f"_scroll: ele_to_scroll should have a content but it is {ele_to_scroll}")
            self.driver.execute_script(cfg.SCROLL_COMMAND, ele_to_scroll)
            print_scroll_num(scroll_num, verbose)
            time.sleep(cfg.SCROLL_PAUSE_TIME)
            try:
                if limit and scroll_num == limit:
                    Log.logger.debug(f"_scroll: finished scrolling")
                    break
                # Finds the bottom of the page
                bot_ele = self.driver.find_element_by_xpath(cfg.BOTTOM_PAGE_XPATH)
            except NoSuchElementException:
                scroll_num += 1
            else:
                time.sleep(cfg.SCROLL_PAUSE_TIME)
                self.driver.execute_script(cfg.SCROLL_COMMAND, bot_ele)
                Log.logger.debug(f"_scroll: finished scrolling")
                break
        Log.logger.info(f"_scroll: finished")

    def _scroll_new_homes(self, limit=None, verbose=False):
        """
        Scrolls down the new_homes url to load all the information available
        """
        scroll_num = 1
        prev_len = len(self.driver.find_elements_by_xpath(cfg.PROPERTIES_XPATH))
        Log.logger.debug(f"_scroll_new_homes:prev_len {prev_len}")
        # maximizing the window makes fewer scrolls necessary
        self.driver.set_window_size(cfg.CHROME_WIDTH, cfg.CHROME_HEIGHT)
        time.sleep(cfg.SCROLL_PAUSE_TIME)
        while True:
            ele_to_scroll = self.driver.find_elements_by_xpath(cfg.PROPERTIES_XPATH)[
                cfg.ELEM_TO_SCROLL_IDX]
            if ele_to_scroll is None:
                Log.logger.error(f"_scroll_new_homes: ele_to_scroll should have a content but it is {ele_to_scroll}")
            self.driver.execute_script(cfg.SCROLL_COMMAND, ele_to_scroll)
            print_scroll_num(scroll_num, verbose)
            time.sleep(cfg.SCROLL_PAUSE_TIME)
            new_len = len(self.driver.find_elements_by_xpath(cfg.PROPERTIES_XPATH))
            if new_len == prev_len or (limit and scroll_num == limit):
                Log.logger.debug(f"_scroll_new_homes: finished scrolling")
                break
            scroll_num += 1
            prev_len = new_len
        Log.logger.info(f"_scroll_new_homes: finished")

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
            self.get_df().to_csv(filename, index=False)
            Log.logger.info(f"_save_to_csv: finished {url}")

    def _save_to_data_base(self, listing_type, verbose=False):
        """
        Save the dataframe containing the scraped info into a database.
        """
        df = self.get_df()
        db_feeder = DataBaeFeeder(df, listing_type, verbose)
        db_feeder.update_db()

    def _print_save_df(self, df, url, to_print=True, save=False, to_database=False, verbose=False, listing_type=None):
        """
        Given a df containing scraped information,
        print it and/or save it to a csv, depending on the user's choice.
        """
        self.update_df(df)
        Log.logger.debug(f"_print_save_df: Checking if print {url},"
                         f" to_print={to_print}, save={save}, to_database={to_database},"
                         f" verbose={verbose}, listing_type={listing_type}")
        if 'project' not in url:
            print_row(self.get_df(), to_print=to_print)
        print_total_items(self.get_df(), verbose=verbose)
        Log.logger.debug(f"_print_to_save: Saving into csv {url},"
                         f" to_print={to_print}, save={save}, to_database={to_database},"
                         f" verbose={verbose}, listing_type={listing_type}")
        self._save_to_csv(url, save=save, verbose=verbose)
        Log.logger.debug(f"_print_to_save: Saving into db {url},"
                         f" to_print={to_print}, save={save}, to_database={to_database},"
                         f" verbose={verbose}, listing_type={listing_type}")
        if to_database:
            self._save_to_data_base(listing_type, verbose=verbose)

        Log.logger.info(f"_print_to_save: finished {url}")

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
        Log.logger.debug(f"scrap_url: Scrolling {url}")
        print_scrolling(url, verbose=kwargs['verbose'])

        if 'project' not in url:
            Log.logger.info(f"scrap_url: Scrolling {url} - not new_homes")
            self._scroll(limit=kwargs['limit'], verbose=kwargs['verbose'])
        else:
            Log.logger.info(f"scrap_url: Scrolling {url} - new_homes")
            self._scroll_new_homes(limit=kwargs['limit'], verbose=kwargs['verbose'])

        print_scraping(url, verbose=kwargs['verbose'])
        Log.logger.debug(f"scrap_url: Scraping {url}")
        html_doc = self.driver.page_source
        soup = bs(html_doc, 'html.parser')
        content = soup.find('div', {'id': 'propertiesList'}).findChildren("div", recursive=False)
        properties_list = content[1].findChildren('div', recursive=False)
        rows_list = []
        Log.logger.debug(f"scrap_url: Creating dataframe from {url}")
        if 'project' not in url:  # for buy, rent and commercial categories
            for proper in properties_list:
                if len(proper.div.div.findChildren('div', recursive=False)) == 2:
                    rows_list.append(property_to_attr_dict(proper, listing_type=kwargs['listing_type']))
            df = pd.DataFrame(rows_list)
            df['Rooms'] = df['Rooms'].astype('float')
            df['Floor'] = df['Floor'].astype('float')
            df['Area'] = df['Area'].astype(np.int64)
            df['Parking_spots'] = df['Parking_spots'].astype(np.int64)
        else:  # for new home category
            for proper in properties_list:
                if len(proper.div.div.findChildren('div', recursive=False)) == 2:
                    rows_list.append(new_home_to_attr_dict(proper, listing_type=kwargs['listing_type']))
            df = pd.DataFrame(rows_list)

        df['City'] = df['City'].str.replace("'", "")
        df['Price'] = df['Price'].astype(np.int64)
        df['latitude'] = None
        df['longitude'] = None
        df['city_hebrew'] = None
        df['address_hebrew'] = None
        df['state_hebrew'] = None

        self._print_save_df(df=df,
                            url=url,
                            to_print=kwargs['to_print'],
                            save=kwargs['save'],
                            verbose=kwargs['verbose'],
                            to_database=kwargs['to_database'],
                            listing_type=kwargs['listing_type'])
        Log.logger.info(f"scrap_url: finished {url}")
