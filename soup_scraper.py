import json
import re

import pandas as pd
import requests
from bs4 import BeautifulSoup as bs

from config import Configuration as cfg
from utils import *


class SoupScraper:

    def __init__(self):
        self._df = None
        self._regional_data = []
        self._urls = []

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

    def append_regional_data(self, url):
        """
        TODO DOCSTRINGS
        """
        self._regional_data.append(url)

    def get_regional_data(self):
        return self._regional_data

    def append_urls(self, url):
        """
        TODO DOCSTRINGS
        """
        self._urls.append(url)

    def get_urls(self):
        return self._urls

    def _get_region_url_list(self, main_url, listing_type, verbose=False):
        """
        Given the main website url and the listing type, returns a list of urls of different regions.
        """
        self._urls = []
        print_getting_url_for_regions(verbose)
        r = requests.get(main_url)
        soup = bs(r.content, 'lxml')
        matches = soup.find_all("input",
                                {
                                    "type": "radio",
                                    'name': "home-page-cities-links",
                                    "value": re.compile(fr".*/{listing_type}/\w+.*")
                                })
        for url in matches:
            self.append_urls(main_url + url['value'])

    def _get_data_from_region(self, listing_type, verbose=False):
        """
        Given a list of urls of different regions and the listing type, updates the regional data list of urls with all
        the properties for this specific listing type, each url for a particular region.
        """
        self._regional_data = []
        print_getting_regional_data(verbose)
        for url in self.get_urls():
            region_name = url.split(cfg.URL_SPLIT_SEPARATOR)[cfg.NOT_SELENIUM_REGION_IDX]
            self.append_regional_data(f'https://phoenix.onmap.co.il/v1/properties/mixed_search?'
                                      f'option={listing_type}&section=residence&'
                                      f'city={region_name}&$sort=-is_top_promoted+-search_date')

    def _transform_to_df(self, limit=None, verbose=False):
        """
        Given a list of urls, each url for a different region, returns a pd.DataFrame with the compiled data from the list.
        The limit, if given, limits the number of properties per region listed in the dataframe.
        """
        print_transform_df(verbose)
        self.update_df(pd.DataFrame(columns=cfg.COLUMNS_NOT_SELENIUM))
        for region in self.get_regional_data():
            if verbose:
                print(region)
            r = requests.get(region)
            soup = bs(r.content, 'lxml')
            property_dict_list = json.loads(soup.p.get_text())['data']
            # num_of_properties counted to limit it if a limit is given
            num_of_properties = 0
            for apartment_dict in property_dict_list:
                num_of_properties += 1
                df_row = create_df_row(apartment_dict)
                self.update_df(pd.concat([self.get_df(), pd.DataFrame(df_row)]))
                if limit is not None:
                    if num_of_properties == limit:
                        break
        # House number and parking spots columns with None and none
        self.update_df(self.get_df().replace(cfg.NONE, cfg.TRIVIAL_NUMBER))
        self.update_df(self.get_df().fillna(value=cfg.TRIVIAL_NUMBER))

    def _save_to_csv(self, listing_type, save=True, verbose=True):
        """
        Save the dataframe containing the scraped info into a csv file
        """
        if save:
            if 'commercial' in listing_type:
                filename = "commercial.csv"
            elif 'projects' in listing_type:
                filename = "new_homes.csv"
            else:
                filename = f"{listing_type}.csv"
            if verbose:
                print(f'\nSaving {filename}\n')
                print(self.get_df())
            self.get_df().to_csv(filename, header=self.get_df().columns, index=False, line_terminator='\n')

    def _print_save_df(self, listing_type, to_print=True, save=False, verbose=False):
        """
        Given a zipped file containing scraped information,
        print it and/or save it to a csv, depending on the user's choice.
        """
        print_row(self.get_df(), to_print=to_print)
        print_total_items(self.get_df(), verbose=verbose)
        self._save_to_csv(listing_type, save=save, verbose=verbose)

    def scrap(self, listing_type, **kwargs):
        """
        Scrapes properties' information given the url and either prints it to the screen and/or save it to a csv file
        ----
        Options available with kwargs:
        to_print: bool
        save: bool
        limit: int (limit of properties per region)
        verbose: bool
        """
        self._get_region_url_list(cfg.MAIN_URL, listing_type, kwargs['verbose'])
        self._get_data_from_region(listing_type, kwargs['verbose'])
        self._transform_to_df(kwargs['limit'], kwargs['verbose'])
        self._print_save_df(listing_type, kwargs['to_print'], kwargs['save'], kwargs['verbose'])

    def __str__(self):
        return self.get_df()
