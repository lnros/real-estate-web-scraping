import re
import string
from hashlib import sha1

from config import Configuration as Cfg
from config import Logger as Log

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
EMPTY_STR = ""
DIGIT_REGEX = r"\d"
# ALL PROPERTIES IN NEW_HOMES LISTING ARE APARTMENTS
NEW_HOMES_PROPERTY_TYPE = 'Apartment'

# logger decorator
KWARGS_KEY_IDX = 0
KWARGS_VALUE_IDX = 1


def generate_id(text):
    """
    Generates an id for the text based on its hash
    ----
    :param text: a unique string to receive a unique hash id
    :type text: str
    :return: a unique hash id
    :rtype: str
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


def new_home_to_attr_dict(buy_property, listing_type):
    """
    :param buy_property: property information scraped from the web
    :type buy_property: bs4.element
    :param listing_type: the listing type of the property: buy, rent, commercial, new home
    :type listing_type: str
    :return: a dataframe-ready row containing the property's information
    :rtype: dict
    """
    proper = buy_property.div.div.findChildren('div', recursive=False)
    string_to_id = []
    price = _return_price(proper)

    string_to_id.append(price)
    attr = proper[ATTR_PROPER_IDX].findChildren('div', recursive=False)

    status = _return_status(attr)
    string_to_id.append(status)

    street = _return_street(attr)
    string_to_id.append(street)
    city = _return_city_new_home(attr)
    string_to_id.append(city)
    string_to_id = EMPTY_STR.join(string_to_id)
    # decided not to use the id for now, handling directly with SQL
    id_ = generate_id(string_to_id)

    type_ = NEW_HOMES_PROPERTY_TYPE

    return {'listing_type': listing_type, 'Property_type': type_, 'City': city,
            'Price': price, 'Address': street, 'ConStatus': status}


def property_to_attr_dict(bs_ele_property, listing_type):
    """
    Getting bs element of single property and returns
    attributes dictionary of the property
    ----
    :param bs_ele_property: property information scraped from the web
    :type bs_ele_property: bs4.element
    :param listing_type: the listing type of the property: buy, rent, commercial, new home
    :type listing_type: str
    :return: a dataframe-ready row containing the property's information
    :rtype: dict
    """
    proper = bs_ele_property.div.div.findChildren('div', recursive=False)
    string_to_id = []
    price = _return_price(proper)
    string_to_id.append(str(price))
    attr = proper[ATTR_PROPER_IDX].findChildren('div', recursive=False)

    type_ = _return_type(attr)
    string_to_id.append(str(type_))
    street = _return_street(attr)
    string_to_id.append(str(street))
    city = _return_city(attr)
    string_to_id.append(str(city))
    rooms = _return_room(attr)
    string_to_id.append(str(rooms))
    floor = _return_floor(attr)
    string_to_id.append(str(floor))
    floor_area = _return_floor_area(attr)
    string_to_id.append(str(floor_area))
    parking = _return_parking(attr)
    string_to_id.append(str(parking))
    string_to_id = "".join(string_to_id)
    # decided not to use the id for now, handling directly with SQL
    id_ = generate_id(string_to_id)

    return {'listing_type': listing_type, 'Property_type': type_, 'City': city, 'Price': price,
            'Address': street,
            'Rooms': rooms, 'Floor': floor, 'Area': floor_area, 'Parking_spots': parking}


def _return_price(prop):
    """
    :param prop: property information
    :type prop: bs4.element
    :return: property's price
    :rtype: str
    """

    try:
        price = prop[PRICE_PROPER_IDX].findChildren('div', recursive=False)[PRICE_CHILDREN_IDX].text
        price = EMPTY_STR.join(re.findall(DIGIT_REGEX, price)).strip()
    except AttributeError:
        price = None
    except KeyError:
        price = None
    except IndexError:
        price = prop[PRICE_PROPER_IDX].findChildren('span', recursive=False)[PRICE_CHILDREN_IDX].text
        price = EMPTY_STR.join(re.findall(DIGIT_REGEX, price)).strip()
    return price


def _return_status(attribute):
    """
    :param attribute: property attributes
    :type attribute: bs4.element
    :return: construction status of new home property
    :rtype: str
    """
    try:
        status = attribute[STATUS_ATTR_IDX].text.strip().split()[STATUS_SPLIT_IDX]
    except AttributeError:
        status = None
    except KeyError:
        status = None
    return status


def _return_street(attribute):
    """
    :param attribute: property attributes
    :type attribute: bs4.element
    :return: property's street
    :rtype: str
    """
    try:
        street = attribute[STREET_ATTR_IDX].text.strip(string.punctuation)
    except AttributeError:
        street = None
    except KeyError:
        street = None
    return street


def _return_city_new_home(attribute):
    """
    :param attribute: property attributes
    :type attribute: bs4.element
    :return: property's city
    :rtype: str
    """
    try:
        city = attribute[NEW_HOME_CITY_ATTR_IDX].text.strip(string.punctuation)
    except AttributeError:
        city = None
    except KeyError:
        city = None
    return city


def _return_city(attribute):
    """
    :param attribute: property attributes
    :type attribute: bs4.element
    :return: property's city
    :rtype: str
    """
    try:
        city = attribute[CITY_ATTR_IDX].text.strip(string.punctuation)
    except AttributeError:
        city = None
    except KeyError:
        city = None
    return city


def _return_type(attribute):
    """
    :param attribute: property attributes
    :type attribute: bs4.element
    :return: property's construction type
    :rtype: str
    """
    try:
        type_ = attribute[TYPE_ATTR_IDX].text.strip(string.punctuation)
    except AttributeError:
        type_ = None
    return type_


def _return_room(attribute):
    """
    :param attribute: property attributes
    :type attribute: bs4.element
    :return: number of rooms in the property
    :rtype: str
    """
    try:
        room = attribute[ROOMS_ATTR_IDX].find('i', {'title': 'Rooms'}).parent.text.strip()
    except AttributeError:
        room = None
    return room


def _return_floor(attribute):
    """
    :param attribute: property attributes
    :type attribute: bs4.element
    :return: number of the floor in which the property is located
    :rtype: str
    """
    try:
        room = attribute[ROOMS_ATTR_IDX].find('i', {'title': 'Rooms'}).parent.text.strip()
    except AttributeError:
        room = None
    return room


def _return_floor_area(attribute):
    """
    :param attribute: property attributes
    :type attribute: bs4.element
    :return: size of the property in sqm
    :rtype: str
    """
    try:
        floor_area = attribute[AREA_ATTR_IDX].find('i', {'title': 'Floor area in sqm'}).parent.text.strip()
    except AttributeError:
        floor_area = None
    return floor_area


def _return_parking(attribute):
    """
    :param attribute: property attributes
    :type attribute: bs4.element
    :return: number of parking spots
    :rtype: str
    """
    try:
        parking = attribute[PARKING_ATTR_IDX].find('i', {'title': 'Parking'}).parent.text.strip()
    except AttributeError:
        parking = 0
    return parking


def print_when_program_finishes():
    print('\nDone!\n')


def print_fetch():
    print('\nFetching more info!\n')


def print_access(url, verbose=True):
    """
    :param url: url address
    :type url: str
    :param verbose: if true, prints which url we will access
    :type verbose: bool
    """
    if verbose:
        print(f'\nAccessing {url}\n')


def print_scrolling(url, verbose=True):
    """
    :param url: url address
    :type url: str
    :param verbose: if true, prints which url we will scroll
    :type verbose: bool
    """
    if verbose:
        print(f"\nScrolling down {url}\n")


def print_scraping(url, verbose=True):
    """
    :param url: url address
    :type url: str
    :param verbose: if true, prints which url we will scrape
    :type verbose: bool
    """
    if verbose:
        print(f"\nScraping {url}\n")


def print_row(df, to_print=True):
    """
    :param df: dataframe containing the information scraped
    :type df: pd.DataFrame
    :param to_print: if true, prints the dataframe row by row
    :type to_print: bool
    """
    if to_print:
        for index, row in df.iterrows():
            print(return_row_before_print(row))


def print_total_items(df, verbose=True):
    """
    :param df: dataframe containing the information scraped
    :type df: pd.DataFrame
    :param verbose: if true, prints the number of items scraped
    :type verbose: bool
    """
    if verbose:
        num_items = len(df)
        print(f'\nScraped total of {num_items} items')


def print_scroll_num(scroll_num, verbose=True):
    """
    :param scroll_num: the current number of times the webpage is being scrolled
    :type scroll_num: int
    :param verbose: if true, prints info to the user before scrolling the webpage
    :type verbose: bool
    """
    if verbose:
        print(f"Scroll nº {scroll_num}")


def print_getting_url_for_regions(verbose=True):
    """
    :param verbose: if true, prints info to the user before calling function that gets url for each region
    :type verbose: bool
    """
    if verbose:
        print("Getting url for each region...")


def print_getting_regional_data(verbose=True):
    """
    :param verbose: if true, prints info to the user before calling function that gets data from each region
    :type verbose: bool
    """
    if verbose:
        print("Getting regional data...")


def print_transform_df(verbose=True):
    """
    :param verbose: if true, prints info to the user before calling function that transforms info into dataframe
    :type verbose: bool
    """
    if verbose:
        print("Transforming the data to dataframe...")


def print_database(verbose=True):
    """
    :param verbose: if true, prints info to the user before calling function that saves info into the database
    :type verbose: bool
    """
    if verbose:
        print("Saving new info into the database...")


def easy_logging(func):
    """
    CURRENTLY NOT WORKING
    TODO: decorator for easy logging when calling functions
    Apparently it already exists: https://pypi.org/project/logdecorator/
    """

    def wrapper(*args, **kwargs):
        Log.logger.debug(f"{func.__name__}: starting")
        for i, arg in enumerate(args):
            Log.logger.debug(f"{func.__name__}: arg {i}: {arg}")
        for i, kwarg in enumerate(kwargs.items()):
            Log.logger.debug(f"{func.__name__}: kwarg {kwarg[KWARGS_KEY_IDX]}: {kwarg[KWARGS_VALUE_IDX]}")
        try:
            if args and kwargs:
                func(*args, **kwargs)
            elif args:
                func(*args)
            elif kwargs:
                func(**kwargs)
            else:
                func()
        except TypeError as err:
            Log.logger.error(f"{func.__name__}: {err}")
        else:
            Log.logger.info(f"{func.__name__}: finished successfully")

    return wrapper


def saving_file(filename):
    """
    :param filename: name of the file we will save after calling this function
    :type filename: str
    """
    return f'\nSaving {filename}\n'
