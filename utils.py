import re
import string
from hashlib import sha1
from config import Configuration as Cfg
from dateutil import parser

# prop_to_attr_dict indices
PRICE_PROPER_IDX = 0
PRICE_CHILDREN_IDX = -1
ATTR_PROPER_IDX = 1
TYPE_ATTR_IDX = 1
STREET_ATTR_IDX = 2
STREET_CHILDREN_IDX = -2
CITY_ATTR_IDX = 2
CITY_CHILDREN_IDX = -1
ROOMS_ATTR_IDX = 3
FLOOR_ATTR_IDX = 3
AREA_ATTR_IDX = 3
PARKING_ATTR_IDX = 3
STATUS_ATTR_IDX = -1
STATUS_SPLIT_IDX = -1
NEW_HOME_CITY_ATTR_IDX = -2

# ALL PROPERTIES IN NEW_HOMES LISTING ARE APARTMENTS
NEW_HOMES_PROPERTY_TYPE = 'Apartment'

def generate_id(text):
    """
    Generates an id for the text based on its hash
    """
    return sha1(str.encode(text)).hexdigest()


def return_row_before_print(row):
    """
    :param row: a row from the properties dataframe
    :type row: pd.Series
    :return: a string with all the values of the row
    :rtype: str
    """
    s = []
    for i in range(len(row)):
        s.append(f"{row.index[i]}: {row[i]}")
    return Cfg.SEPARATOR.join(s)


def create_df_row(property_dict):
    """
    Given a dictionary with property information, transform it into a dictionary to be used as a dataframe row
    """
    try:
        df_row = {'Date': [parser.parse(property_dict['created_at']).date()],
                  'City_name': [property_dict['address']['en']['city_name']],
                  'Street_name': [property_dict['address']['en']['street_name']],
                  'House_number': [property_dict['address']['en']['house_number']],
                  'Bathrooms': [property_dict['additional_info']['bathrooms']],
                  'Rooms': [property_dict['additional_info']['rooms']],
                  'Floor': [property_dict['additional_info']['floor']['on_the']],
                  'Area[m^2]': [property_dict['additional_info']['area']['base']],
                  'Parking_spots_aboveground': [
                      property_dict['additional_info'].get('parking', {}).get('aboveground')],
                  'Parking_spots_underground': [
                      property_dict['additional_info'].get('parking', {}).get('underground')],
                  'Price[NIS]': [property_dict['price']],
                  'Property_type': [property_dict['property_type']]
                  }
        return df_row
    except KeyError:
        # TODO Take care of new project in buy
        pass


def new_home_to_attr_dict(buy_property, listing_type):
    proper = buy_property.div.div.findChildren('div', recursive=False)
    string_to_id = []
    try:
        price = proper[PRICE_PROPER_IDX].findChildren('div', recursive=False)[PRICE_CHILDREN_IDX].text
        price = ''.join(re.findall("\d", price)).strip()
    except:
        price = None

    string_to_id.append(price)
    attr = proper[ATTR_PROPER_IDX].findChildren('div', recursive=False)

    try:
        Status = attr[STATUS_ATTR_IDX].text.strip().split()[STATUS_SPLIT_IDX]
    except:
        Status = None
    string_to_id.append(Status)

    try:
        street = attr[STREET_ATTR_IDX].text.strip(string.punctuation)
    except:
        street = None
    string_to_id.append(street)
    try:
        city = attr[NEW_HOME_CITY_ATTR_IDX].text.strip(string.punctuation)
    except:
        city = None
    string_to_id.append(city)
    string_to_id = "".join(string_to_id)
    id_ = generate_id(string_to_id)

    type_ = NEW_HOMES_PROPERTY_TYPE

    return {'listing_type': listing_type, 'Property_type': type_, 'City': city,
            'Price': price, 'Address': street, 'ConStatus': Status}


def property_to_attr_dict(bs_ele_property, listing_type):
    """
    getting bs element of single property and returns
    attributes dictionary of the property"""
    proper = bs_ele_property.div.div.findChildren('div', recursive=False)
    string_to_id = []
    try:
        price = proper[PRICE_PROPER_IDX].findChildren('span', recursive=False)[PRICE_CHILDREN_IDX].text
        price = ''.join(re.findall("\d", price)).strip()
    except AttributeError:
        price = None
    string_to_id.append(str(price))
    attr = proper[ATTR_PROPER_IDX].findChildren('div', recursive=False)

    try:
        type_ = attr[TYPE_ATTR_IDX].text.strip(string.punctuation)
    except AttributeError:
        type_ = None
    string_to_id.append(str(type_))
    try:
        street = attr[STREET_ATTR_IDX].findChildren('div', recursive=False)[STREET_CHILDREN_IDX].text.strip(
            string.punctuation)
    except AttributeError:
        street = None
    string_to_id.append(str(street))
    try:
        city = attr[CITY_ATTR_IDX].findChildren('div', recursive=False)[CITY_CHILDREN_IDX].text.strip(
            string.punctuation)
    except AttributeError:
        city = None
    string_to_id.append(str(city))
    try:
        rooms = attr[ROOMS_ATTR_IDX].find('i', {'title': 'Rooms'}).parent.text.strip()
    except AttributeError:
        rooms = None
    string_to_id.append(str(rooms))
    try:
        floor = attr[FLOOR_ATTR_IDX].find('i', {'title': 'Floor'}).parent.text.strip()
    except AttributeError:
        floor = None
    string_to_id.append(str(floor))
    try:
        floor_area = attr[AREA_ATTR_IDX].find('i', {'title': 'Floor area in sqm'}).parent.text.strip()
    except AttributeError:
        floor_area = None
    string_to_id.append(str(floor_area))
    try:
        parking = attr[PARKING_ATTR_IDX].find('i', {'title': 'Parking'}).parent.text.strip()
    except AttributeError:
        parking = 0
    string_to_id.append(str(parking))
    string_to_id = "".join(string_to_id)
    id_ = generate_id(string_to_id)

    return {'listing_type': listing_type, 'Property_type': type_, 'City': city, 'Price': price,
            'Address': street,
            'Rooms': rooms, 'Floor': floor, 'Area': floor_area, 'Parking_spots': parking}


def print_when_program_finishes():
    print('\nDone!\n')

def print_fetch():
    print('\nFetching more info!\n')

def print_access(url, verbose=True):
    if verbose:
        print(f'\nAccessing {url}\n')


def print_scrolling(url, verbose=True):
    if verbose:
        print(f"\nScrolling down {url}\n")


def print_scraping(url, verbose=True):
    if verbose:
        print(f"\nScraping {url}\n")


def print_row(df, to_print=True):
    if to_print:
        for index, row in df.iterrows():
            print(return_row_before_print(row))


def print_total_items(df, verbose=True):
    if verbose:
        num_items = len(df)
        print(f'\nScraped total of {num_items} items')


def print_scroll_num(scroll_num, verbose=True):
    if verbose:
        print(f"Scroll nº {scroll_num}")


def print_getting_url_for_regions(verbose=True):
    if verbose:
        print("Getting url for each region...")


def print_getting_regional_data(verbose=True):
    if verbose:
        print("Getting regional data...")


def print_transform_df(verbose=True):
    if verbose:
        print("Transforming the data to dataframe...")


def print_database(verbose=True):
    if verbose:
        print("Saving new info into the database...")
