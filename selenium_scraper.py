import os
import time
from bs4 import BeautifulSoup as bs
import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import pymysql
from config import Configuration as cfg
from utils import *


def create_driver():
    """
    Creates a driver that runs in Google Chrome.
    """
    os.environ['WDM_LOG_LEVEL'] = cfg.SILENCE_DRIVER_LOG
    return webdriver.Chrome(ChromeDriverManager().install())


def new_home_to_attr_dict(buy_property, listing_type):
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

    return {'listing_type': listing_type, 'Price': price, 'City': city, 'Address': street, 'Status': Status}


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
            if scroll_num == 3:
                break
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
            self.get_df().to_csv(filename, index=False)

    def _save_to_data_base(self, listing_type):
        """
        Save the dataframe containing the scraped info into a database.
        """
        df = self.get_df()
        df = df.replace(np.nan, None)

        connection = pymysql.connect("localhost", "root", "password", "on_map")
        cursor = connection.cursor()

        for city in df['City'].unique():
            sql_query = ("INSERT IGNORE INTO cities(city_name) values (%s)")
            cursor.execute(sql_query, city)

        for listing in df['listing_type'].unique():
            sql_query = ("INSERT IGNORE INTO listings(listing_type) values (%s)")
            cursor.execute(sql_query, listing)

        if listing_type != 'new homes':
            for Property in df['Property_type'].unique():
                sql_query = ("INSERT IGNORE INTO property_types(property_type) values (%s)")
                cursor.execute(sql_query, Property)

        connection.commit()

        cols = ",".join([str(i) for i in df.columns.tolist()])

        if listing_type != 'new homes':
            sql = f"DELETE FROM properties WHERE listing_type = '{listing_type}'"
            cursor.execute(sql)
            for i, row in df.iterrows():
                sql = "INSERT INTO properties (" + cols + ") VALUES (" + "%s," * (len(row) - 1) + "%s)"
                cursor.execute(sql, tuple(row))
            # sql = f"ALTER TABLE properties AUTO_INCREMENT = 1"
            # sql = "SET @num := 0; UPDATE properties id = @num := (@num+1);"
            sql = "SELECT id FROM properties ORDER BY id LIMIT 1"
            cursor.execute(sql)
            curr_lowest_id = cursor.fetchone()[0]
            sql = f"UPDATE properties SET id = id - {curr_lowest_id} + 1;"
            cursor.execute(sql)
        else:
            sql = f"DELETE FROM new_homes WHERE listing_type = '{listing_type}'"
            cursor.execute(sql)
            for i, row in df.iterrows():
                sql = "INSERT INTO new_homes (" + cols + ") VALUES (" + "%s," * (len(row) - 1) + "%s)"
                cursor.execute(sql, tuple(row))
            # sql = f"ALTER TABLE new_homes AUTO_INCREMENT = 1"
            # sql = "SET @num := 0; UPDATE new_homes SET id = @num := (@num+1);"
            sql = "SELECT id FROM new_homes ORDER BY id LIMIT 1"
            cursor.execute(sql)
            curr_lowest_id = cursor.fetchone()[0]
            sql = f"UPDATE new_homes SET id = id - {curr_lowest_id} + 1;"
            cursor.execute(sql)

        connection.commit()

    def _print_save_df(self, df, url, to_print=True, save=False, verbose=False, listing_type=None):
        """
        Given a df containing scraped information,
        print it and/or save it to a csv, depending on the user's choice.
        """
        self.update_df(df)
        if 'project' not in url:
            print_row(self.get_df(), to_print=to_print)
        print_total_items(self.get_df(), verbose=verbose)
        self._save_to_csv(url, save=save, verbose=verbose)
        self._save_to_data_base(listing_type)

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
                    rows_list.append(property_to_attr_dict(proper, listing_type=kwargs['listing_type']))
            df = pd.DataFrame(rows_list)
            df['Price'] = df['Price'].astype(np.int64)
            df['Rooms'] = df['Rooms'].astype('float')
            df['Floor'] = df['Floor'].astype('float')
            df['Area'] = df['Area'].astype(np.int64)
            df['Parking_spots'] = df['Parking_spots'].astype(np.int64)
        else:  # for new home category
            for proper in properties_list:
                if len(proper.div.div.findChildren('div', recursive=False)) == 2:
                    rows_list.append(new_home_to_attr_dict(proper, listing_type=kwargs['listing_type']))
            df = pd.DataFrame(rows_list)
            df['Price'] = df['Price'].astype(np.int64)

        self._print_save_df(df, url, to_print=kwargs['to_print'], save=kwargs['save'],
                            verbose=kwargs['verbose'], listing_type=kwargs['listing_type'])
