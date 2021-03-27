import re
import string
from config import Configuration as Cfg
from config import Logger as Log
from dateutil import parser
from hashlib import sha1

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
    proper = buy_property.div.div.findChildren('div', recursive=False)
    string_to_id = []
    price = _return_price(proper)

    string_to_id.append(price)
    attr = proper[ATTR_PROPER_IDX].findChildren('div', recursive=False)

    status = _return_status(attr)
    string_to_id.append(Status)

    street = _return_street(attr)
    string_to_id.append(street)
    city = _return_city(attr)
    string_to_id.append(city)
    string_to_id = "".join(string_to_id)
    id_ = generate_id(string_to_id)

    type_ = NEW_HOMES_PROPERTY_TYPE

    return {'listing_type': listing_type, 'Property_type': type_, 'City': city,
            'Price': price, 'Address': street, 'ConStatus': status}


def property_to_attr_dict(bs_ele_property, listing_type):
    """
    getting bs element of single property and returns
    attributes dictionary of the property"""
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
    id_ = generate_id(string_to_id)

    return {'listing_type': listing_type, 'Property_type': type_, 'City': city, 'Price': price,
            'Address': street,
            'Rooms': rooms, 'Floor': floor, 'Area': floor_area, 'Parking_spots': parking}


def _return_price(property):
    """
    TODO
    """
    try:
        price = property[PRICE_PROPER_IDX].findChildren('div', recursive=False)[PRICE_CHILDREN_IDX].text
        price = EMPTY_STR.join(re.findall(DIGIT_REGEX, price)).strip()
    except AttributeError:
        price = None
    except KeyError:
        price = None
    except IndexError as exc:
        price = property[PRICE_PROPER_IDX].findChildren('span', recursive=False)[PRICE_CHILDREN_IDX].text
        price = EMPTY_STR.join(re.findall(DIGIT_REGEX, price)).strip()
    return price


def _return_status(attribute):
    """
    TODO
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
    TODO
    """
    try:
        street = attribute[STREET_ATTR_IDX].text.strip(string.punctuation)
    except AttributeError:
        street = None
    except KeyError:
        street = None
    return street


def _return_city(attribute):
    """
    TODO
    """
    try:
        city = attribute[NEW_HOME_CITY_ATTR_IDX].text.strip(string.punctuation)
    except AttributeError:
        city = None
    except KeyError:
        city = None
    return city


def _return_type(attribute):
    """
    TODO
    """
    try:
        type_ = attribute[TYPE_ATTR_IDX].text.strip(string.punctuation)
    except AttributeError:
        type_ = None
    return type_


def _return_room(attribute):
    """
    TODO
    """
    try:
        room = attribute[ROOMS_ATTR_IDX].find('i', {'title': 'Rooms'}).parent.text.strip()
    except AttributeError:
        room = None
    return room


def _return_floor(attribute):
    """
    TODO
    """
    try:
        room = attribute[ROOMS_ATTR_IDX].find('i', {'title': 'Rooms'}).parent.text.strip()
    except AttributeError:
        room = None
    return room


def _return_floor_area(attribute):
    """
    TODO
    """
    try:
        floor_area = attribute[AREA_ATTR_IDX].find('i', {'title': 'Floor area in sqm'}).parent.text.strip()
    except AttributeError:
        floor_area = None
    return floor_area


def _return_parking(attribute):
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


def easy_logging(func):
    """
    NOT WORKING, TODO
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
    return f'\nSaving {filename}\n'
