import asyncio
import os
import time
from socket import timeout

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup as bs
from geopy.exc import GeocoderUnavailable, GeocoderTimedOut
from requests.exceptions import ConnectionError
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from tqdm import tqdm
from urllib3.exceptions import MaxRetryError, ReadTimeoutError
from webdriver_manager.chrome import ChromeDriverManager

from config import GeoFetcherConfig
from config import Logger as Log
from data_base_feeder import DataBaseFeeder
from geofetcher import GeoFetcher
from utils import *


class SeleniumScraper:
    """
    This class scrapes the website "On Map", fetches more information available,
    and with the information scraped it can:
    - Print it to the user
    - Save it to csv
    - Save into a database
    Notice that we also use BeautifulSoup after we use Selenium to scroll the url
    """

    def __init__(self):
        self.driver = self._create_driver()
        self._df = None

    @staticmethod
    def _create_driver():
        """
        Creates a driver that runs in Google Chrome.
        """
        os.environ['WDM_LOG_LEVEL'] = Cfg.SILENCE_DRIVER_LOG
        return webdriver.Chrome(ChromeDriverManager().install())

    def update_df(self, df):
        """
        Updates the dataframe containing the scraped info
        ----
        :type df: pd.Dataframe
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
        ----
        :param limit: limits the number of scrolling per page
        :type limit: int
        :param verbose: if true, it prints relevant information to the user
        :type verbose: bool
        """
        scroll_num = 1
        # maximizing the window makes fewer scrolls necessary
        self.driver.set_window_size(Cfg.CHROME_WIDTH, Cfg.CHROME_HEIGHT)
        time.sleep(Cfg.SCROLL_PAUSE_TIME)
        while True:
            ele_to_scroll = self.driver.find_elements_by_xpath(Cfg.PROPERTIES_XPATH)[
                Cfg.ELEM_TO_SCROLL_IDX]
            if ele_to_scroll is None:
                Log.logger.error(Log.scroll_error(ele_to_scroll))
            self.driver.execute_script(Cfg.SCROLL_COMMAND, ele_to_scroll)
            print_scroll_num(scroll_num, verbose)
            time.sleep(Cfg.SCROLL_PAUSE_TIME)
            try:
                if limit and scroll_num == limit:
                    Log.logger.debug(Log.scroll_finished)
                    break
                # Finds the bottom of the page
                bot_ele = self.driver.find_element_by_xpath(Cfg.BOTTOM_PAGE_XPATH)
            except NoSuchElementException:
                scroll_num += 1
            else:
                time.sleep(Cfg.SCROLL_PAUSE_TIME)
                self.driver.execute_script(Cfg.SCROLL_COMMAND, bot_ele)
                Log.logger.debug(Log.scroll_finished)
                break
        Log.logger.info(Log.end_scroll_function)

    def _scroll_new_homes(self, limit=None, verbose=False):
        """
        Scrolls down the new_homes url to load all the information available
        ----
        :param limit: limits the number of scrolling per page
        :type limit: int
        :param verbose: if true, it prints relevant information to the user
        :type verbose: bool
        """
        scroll_num = 1
        prev_len = len(self.driver.find_elements_by_xpath(Cfg.PROPERTIES_XPATH))
        Log.logger.debug(Log.scroll_new_homes(prev_len))
        # maximizing the window makes fewer scrolls necessary
        self.driver.set_window_size(Cfg.CHROME_WIDTH, Cfg.CHROME_HEIGHT)
        time.sleep(Cfg.SCROLL_PAUSE_TIME)
        while True:
            ele_to_scroll = self.driver.find_elements_by_xpath(Cfg.PROPERTIES_XPATH)[
                Cfg.ELEM_TO_SCROLL_IDX]
            if ele_to_scroll is None:
                Log.logger.error(Log.scroll_error(ele_to_scroll))
            self.driver.execute_script(Cfg.SCROLL_COMMAND, ele_to_scroll)
            print_scroll_num(scroll_num, verbose)
            time.sleep(Cfg.SCROLL_PAUSE_TIME)
            new_len = len(self.driver.find_elements_by_xpath(Cfg.PROPERTIES_XPATH))
            if new_len == prev_len or (limit and scroll_num == limit):
                Log.logger.debug(Log.scroll_finished_new_home)
                break
            scroll_num += 1
            prev_len = new_len
        Log.logger.info(Log.end_scroll_new_home)

    def _save_to_csv(self, url, save=True, verbose=True):
        """
        Save the dataframe containing the scraped info into a csv file
        ----
        :param url: url address
        :type url: str
        :param save: if true, it saves the dataframe into a csv file
        :type save: bool
        :param verbose: if true, it prints relevant information to the user
        :type verbose: bool
        """
        if save:
            if Cfg.COMMERCIAL in url:
                filename = Cfg.COMMERCIAL_FILENAME
            elif Cfg.PROJECT in url:
                filename = Cfg.NEW_HOMES_FILENAME
            else:
                filename = f"{url.split(Cfg.URL_SPLIT_SEPARATOR)[Cfg.FILENAME_IDX]}.csv"
            if verbose:
                print(saving_file(filename))
            self.get_df().to_csv(filename, index=False, encoding=Cfg.ENCODING)
            Log.logger.info(Log.end_save_csv(url))

    def _save_to_data_base(self, listing_type, to_database=True, verbose=False):
        """
        Save the dataframe containing the scraped info into a database.
        ----
        :param listing_type: type of listing: buy, rent, commercial, new_home
        :type listing_type: str
        :param to_database: if true, it saves the new information from the dataframe to the database
        :type to_database: bool
        :param verbose: if true, it prints relevant information to the user
        :type verbose: bool
        """
        if to_database:
            df = self.get_df()
            db_feeder = DataBaseFeeder(df, listing_type, verbose)
            db_feeder.update_db()

    def _print_save_df(self, url, to_print=True, save=False, to_database=False, verbose=False, listing_type=None):
        """
        Given a df containing scraped information,
        print it and/or save it to a csv, depending on the user's choice.
        ----
        :param url: url address
        :type url: str
        :param listing_type: type of listing: buy, rent, commercial, new_home
        :type listing_type: str
        :param to_print: if true, it prints the dataframe to the screen
        :type to_print: bool
        :param save: if true, it saves the dataframe into a csv file
        :type save: bool
        :param to_database: if true, it saves the new information from the dataframe to the database
        :type to_database: bool
        :param verbose: if true, it prints relevant information to the user
        :type verbose: bool
        """
        Log.logger.debug(Log.init_print_save_df(url, to_print, save, to_database, verbose, listing_type))
        if Cfg.PROJECT not in url:
            print_row(self.get_df(), to_print=to_print)
        print_total_items(self.get_df(), verbose=verbose)
        Log.logger.debug(Log.saving_print_save_df(url, to_print, save, to_database, verbose, listing_type))
        self._save_to_csv(url, save=save, verbose=verbose)
        Log.logger.debug(Log.db_print_save_df(url, to_print, save, to_database, verbose, listing_type))
        self._save_to_data_base(listing_type, to_database=to_database, verbose=verbose)
        Log.logger.info(Log.end_print_save(url))

    def _fetch_more_attributes(self, fetch_info=True, verbose=False):
        """
        Uses Geopy with Nominatim service to fetch more information on the property location asynchronously.
        ----
        :param fetch_info: Whether or not we want to fetch more information
        :type fetch_info: bool
        :param verbose: Whether or not we want to print extensive information of what is happening to the user
        :type verbose: bool
        :return: a new dataframe with the new fetched information added
        :rtype: Dataframe
        """
        if fetch_info:
            Log.logger.debug(Log.fetch_more_init)
            df_new = self.get_df().copy()
            gf = GeoFetcher()
            Log.logger.info(Log.geofetcher_init)
            if verbose:
                print_fetch()
            for i, row in tqdm(df_new.iterrows(), total=len(df_new), disable=(not verbose)):
                Log.logger.debug(Log.pulling_row_info(i))
                try:
                    df_new.iloc[i] = asyncio.run(gf.pull_row_info(row))
                # Nominatim is a free API that doesn't allow multiple requests without errors
                # Using delay may not be enough in some cases
                except GeocoderTimedOut as err:
                    Log.logger.error(Log.exception_fetch_more_attributes(row_number=i, exception=err))
                    df_new.iloc[i] = self.get_df().iloc[i]
                except GeocoderUnavailable as err:
                    Log.logger.error(Log.exception_fetch_more_attributes(row_number=i, exception=err))
                    df_new.iloc[i] = self.get_df().iloc[i]
                except MaxRetryError as err:
                    Log.logger.error(Log.exception_fetch_more_attributes(row_number=i, exception=err))
                    df_new.iloc[i] = self.get_df().iloc[i]
                except ConnectionError as err:
                    Log.logger.error(Log.exception_fetch_more_attributes(row_number=i, exception=err))
                    df_new.iloc[i] = self.get_df().iloc[i]
                except ReadTimeoutError as err:
                    Log.logger.error(Log.exception_fetch_more_attributes(row_number=i, exception=err))
                    df_new.iloc[i] = self.get_df().iloc[i]
                except timeout as err:
                    Log.logger.error(Log.exception_fetch_more_attributes(row_number=i, exception=err))
                    df_new.iloc[i] = self.get_df().iloc[i]
            Log.logger.info(Log.end_fetch_more_att)
            return df_new
        else:
            Log.logger.debug(Log.not_fetched(fetch_info))

    @staticmethod
    def _create_df(url, properties_list, **kwargs):
        """
        Creates a dataframe based on the properties scraped
        ----
        :param url: url from which we scraped
        :type url: string
        :param properties_list: list of bs4.elements with information scraped from the web
        :type properties_list: list
        :param kwargs: hyperparameters chosen by the user
        :type kwargs: dict
        :return: The properties' dataframe
        :rtype: Dataframe
        """
        Log.logger.debug(Log.creating_df(url))
        rows_list = []
        if Cfg.PROJECT not in url:  # for buy, rent and commercial categories
            for proper in properties_list:
                if len(proper.div.div.findChildren('div', recursive=False)) == Cfg.LEN_PROPER:
                    rows_list.append(property_to_attr_dict(proper, listing_type=kwargs[Cfg.LISTING_TYPE_KEY]))
            df = pd.DataFrame(rows_list)
            # Replacing empty strings so we can convert columns to correct type
            for col in df.columns:
                df[col] = df[col].replace(Cfg.EMPTY, Cfg.DUMMY_REPLACER)
            df[Cfg.PRICE_COL] = df[Cfg.PRICE_COL].astype(np.int64)
            df[Cfg.ROOM_COL] = df[Cfg.ROOM_COL].astype('float')
            df[Cfg.FLOOR_COL] = df[Cfg.FLOOR_COL].astype('float')
            df[Cfg.AREA_COL] = df[Cfg.AREA_COL].astype(np.int64)
            df[Cfg.PARKING_COL] = df[Cfg.PARKING_COL].astype(np.int64)

        else:  # for new home category
            for proper in properties_list:
                if len(proper.div.div.findChildren('div', recursive=False)) == Cfg.LEN_PROPER:
                    rows_list.append(new_home_to_attr_dict(proper, listing_type=kwargs[Cfg.LISTING_TYPE_KEY]))
            df = pd.DataFrame(rows_list)

        df[GeoFetcherConfig.LAT_KEY] = None
        df[GeoFetcherConfig.LON_KEY] = None
        df[GeoFetcherConfig.CITY_HEBREW_KEY] = None
        df[GeoFetcherConfig.ADDRESS_HEBREW_KEY] = None
        df[GeoFetcherConfig.STATE_HEBREW_KEY] = None
        Log.logger.info(Log.created_df(url))

        return df

    def scrap_url(self, url, **kwargs):
        """
        Scrapes properties' information given the url and either prints it to the screen and/or save it to a csv file
        ----
        Options available with kwargs:
        limit: bool
        to_print: bool
        save: bool
        verbose: bool
        to_database: bool
        fetch_info: bool
        listing_type: a list containing at least one of the following: 'buy', 'rent', 'commercial', 'new homes'
        """
        print_access(url, verbose=kwargs[Cfg.VERBOSE_KEY])
        self.driver.get(url)
        Log.logger.debug(Log.scraping(url))
        print_scrolling(url, verbose=kwargs[Cfg.VERBOSE_KEY])

        if Cfg.PROJECT not in url:
            Log.logger.info(Log.before_scroll)
            self._scroll(limit=kwargs[Cfg.LIMIT_KEY], verbose=kwargs[Cfg.VERBOSE_KEY])
        else:
            Log.logger.info(Log.before_scroll_new_home(url))
            self._scroll_new_homes(limit=kwargs[Cfg.LIMIT_KEY], verbose=kwargs[Cfg.VERBOSE_KEY])

        print_scraping(url, verbose=kwargs[Cfg.VERBOSE_KEY])
        Log.logger.debug(Log.before_scraping(url))
        html_doc = self.driver.page_source
        soup = bs(html_doc, 'html.parser')
        content = soup.find('div', Cfg.DICT_PROPERTY_ID).findChildren("div", recursive=False)
        properties_list = content[Cfg.PROPERTIES_LIST_IDX].findChildren('div', recursive=False)
        self.update_df(self._create_df(url, properties_list, **kwargs))
        if kwargs[Cfg.FETCH_KEY]:
            self.update_df(self._fetch_more_attributes(fetch_info=kwargs[Cfg.FETCH_KEY],
                                                       verbose=kwargs[Cfg.VERBOSE_KEY]))
        self._print_save_df(url=url,
                            to_print=kwargs[Cfg.PRINT_KEY],
                            save=kwargs[Cfg.SAVE_KEY],
                            verbose=kwargs[Cfg.VERBOSE_KEY],
                            to_database=kwargs[Cfg.DB_KEY],
                            listing_type=kwargs[Cfg.LISTING_TYPE_KEY])
        Log.logger.info(Log.finished_scraping(url))
