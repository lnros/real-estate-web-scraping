import argparse
import json
import os
import re

import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
from dateutil import parser

URL = 'https://www.onmap.co.il/en'
COLUMNS = ['Date', 'City_name', 'Street_name', 'House_number', 'Bathrooms', 'Rooms', 'Floor', 'Area[m^2]',
           'Parking_spots_aboveground', 'Parking_spots_underground', 'Price[NIS]', 'Property_type']
PROPERTY_LISTING_TYPE = ('buy', 'rent', 'all')


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
    arg_parser.add_argument('--limit', '-l', help="limit to n number of properties per region", metavar="n", type=int,
                            required=False)
    arg_parser.add_argument("--todir", help="save the scraped information into a csv file in the given directory",
                            metavar="path",
                            type=str, required=False)
    return arg_parser.parse_args()


def get_region_url_list(main_url, rent_or_sale):
    """
    Given the main website url and the listing type (buy or rent), returns a list of urls of different regions.
    """
    r = requests.get(main_url)
    soup = bs(r.content, 'lxml')
    urls = []
    matches = soup.find_all("input",
                            {
                                "type": "radio",
                                'name': "home-page-cities-links",
                                "value": re.compile(fr".*/{rent_or_sale}/\w+.*")
                            })
    for url in matches:
        urls.append(main_url + url['value'])
    return urls


def get_data_from_region(region_url_list, rent_or_sale):
    """
    Given a list of urls of different regions and the listing type (rent or buy), returns a list of urls with all
    the properties for this specific listing type, each url for a particular region.
    """
    regional_data = []
    for url in region_url_list:
        region_name = url.split('/')[-1]
        regional_data.append(
            f'https://phoenix.onmap.co.il/v1/properties/mixed_search?'
            f'option={rent_or_sale}&section=residence&city={region_name}&$sort=-is_top_promoted+-search_date')
    return regional_data


def transform_to_df(regional_data, limit=None):
    """
    Given a list of urls, each url for a different region, returns a pd.DataFrame with the compiled data from the list.
    The limit, if given, limits the number of properties per region listed in the dataframe.
    """
    df = pd.DataFrame(columns=COLUMNS)
    for region in regional_data:
        r = requests.get(region)
        soup = bs(r.content, 'lxml')
        property_dict_list = json.loads(soup.p.get_text())['data']
        # num_of_properties counted to limit it if a limit is given
        num_of_properties = 0
        for apartment_dict in property_dict_list:
            num_of_properties += 1
            df_row = {'Date': [parser.parse(apartment_dict['created_at']).date()],
                      'City_name': [apartment_dict['address']['en']['city_name']],
                      'Street_name': [apartment_dict['address']['en']['street_name']],
                      'House_number': [apartment_dict['address']['en']['house_number']],
                      'Bathrooms': [apartment_dict['additional_info']['bathrooms']],
                      'Rooms': [apartment_dict['additional_info']['rooms']],
                      'Floor': [apartment_dict['additional_info']['floor']['on_the']],
                      'Area[m^2]': [apartment_dict['additional_info']['area']['base']],
                      'Parking_spots_aboveground': [
                          apartment_dict['additional_info'].get('parking', {}).get('aboveground')],
                      'Parking_spots_underground': [
                          apartment_dict['additional_info'].get('parking', {}).get('underground')],
                      'Price[NIS]': [apartment_dict['price']],
                      'Property_type': [apartment_dict['property_type']]
                      }
            df = pd.concat([df, pd.DataFrame(df_row)])
            if limit is not None:
                if num_of_properties == limit:
                    break
    # House number and parking spots columns with None and none
    df = df.replace('none', 0)
    df = df.fillna(value=0)
    return df


def save_to_csv(df, filepath):
    """
    Given a pd.DataFrame and the directory filepath as string, saves the dataframe as a csv file in the filepath given.
    """
    with open(filepath, 'w') as f:
        df.to_csv(f, header=df.columns, index=False, line_terminator='\n')


def main():
    """
    Given the user input, either print or save to a csv file buy and/or rent real estate
    scraped data from the OnMap website
    """
    args = define_parser()
    listing_type = {
        'buy': ['buy'],
        'rent': ['rent'],
        'all': ['buy', 'rent']
    }

    if args.property_listing_type not in PROPERTY_LISTING_TYPE:
        print(f'You should choose of one the following: {PROPERTY_LISTING_TYPE},'
              f' but you provided {args.property_listing_type}')
        return
    if not os.path.isdir(args.todir.split('.')[0]) and args.todir:
        print('The path provided is not a directory.')
        return

    if args.limit:
        limit = args.limit
    else:
        limit = None

    for rent_or_sale in listing_type[args.property_listing_type]:
        region_url_list = get_region_url_list(URL, rent_or_sale)
        region_data = get_data_from_region(region_url_list, rent_or_sale)
        listing_df = transform_to_df(region_data, limit)
        if args.todir:
            filepath = args.todir.split('.')[0] + f'{rent_or_sale}' + '.csv'
            save_to_csv(listing_df, filepath)
        else:
            print(20 * '#' + f' {rent_or_sale.upper()} ' + 20 * '#')
            print(listing_df)


if __name__ == '__main__':
    main()
