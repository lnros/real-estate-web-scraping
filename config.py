import argparse
import logging
import string
import sys


class GeoFetcherConfig:
    SEPARATOR = ", "
    ADDRESS_KEY = 'address'
    CITY_KEY = 'city'
    STATE_KEY = 'state'
    LAT_KEY = 'latitude'
    LON_KEY = 'longitude'
    ROAD_KEY = 'road'
    CITY_HEBREW_KEY = 'city_hebrew'
    ADDRESS_HEBREW_KEY = 'address_hebrew'
    STATE_HEBREW_KEY = 'state_hebrew'
    ADDRESS_ERR_MSG = "address should be str"
    ROW_ADDRESS_KEY = 'Address'
    ROW_CITY_KEY = 'City'
    DELAY_TIME = 1
    USER_AGENT = "on_map"
    WHITESPACE = " "


class DBConfig:
    """
    Holds the DB parameters for the web scraping.
    """

    HOST = "brbeky1hybvf32t4ufxz-mysql.services.clever-cloud.com"
    USER = "uydbyi6qdkmbhd4q"
    PASSWORD = "GXB67Y5tnWYyewKEZ0OW"
    DATABASE = "brbeky1hybvf32t4ufxz"


class Configuration:
    """
    Holds the user parameters for the web scraping.
    """

    # class attr
    args = None

    # CONSTANTS FOR SCRAPING
    PRINTABLE = set(string.printable)
    SILENCE_DRIVER_LOG = '0'
    CHROME_WIDTH = 1919
    CHROME_HEIGHT = 1079
    PROPERTY_LISTING_TYPE = ('buy', 'rent', 'commercial', 'new_homes', 'all')
    LISTING_MAP = {
        'buy': ['buy'],
        'rent': ['rent'],
        'commercial': ['commercial'],
        'new_homes': ['new homes'],
        'all': ['buy', 'rent', 'commercial', 'new homes']
    }
    MAIN_URL = 'https://www.onmap.co.il/en'
    URLS = {'buy': MAIN_URL + '/homes/buy',
            'rent': MAIN_URL + '/homes/rent',
            'commercial': MAIN_URL + '/commercial/rent',
            'new homes': MAIN_URL + '/projects'}

    COLUMNS_NOT_SELENIUM = ['Date', 'City_name', 'Street_name', 'House_number', 'Bathrooms', 'Rooms', 'Floor',
                            'Area[m^2]',
                            'Parking_spots_aboveground', 'Parking_spots_underground', 'Price[NIS]', 'Property_type']
    SCROLL_PAUSE_TIME = 1
    BETWEEN_URL_PAUSE = 3
    SINGLE_ATR_ITEM = 1
    TRIVIAL_NUMBER = 0
    INVALID_FLOOR_TEXT_SIZE = 1
    NOT_SELENIUM_PRINTING_HASH_CONSTANT = 20
    NONE = 'none'
    # INDICES FOR PARSING
    NOT_SELENIUM_PARSING_FILE_IDX = 0
    ELEM_TO_SCROLL_IDX = -1
    PRICE_IDX = -1
    CITY_IDX = -1
    ADDRESS_IDX = -2
    PROPERTY_TYPE_IDX = 1
    NUM_OF_ROOMS_IDX = 0
    FLOOR_IDX = 1
    SIZE_IDX = 2
    PARKING_SPACES_IDX = 3
    FILENAME_IDX = -1
    SIZE_TEXT_IDX = 0
    NOT_SELENIUM_REGION_IDX = -1
    URL_SPLIT_SEPARATOR = '/'
    NOT_SELENIUM_SEPARATOR = '.'
    SEPARATOR = ", "

    # XPATHS AND SELENIUM COMMANDS
    SCROLL_COMMAND = "arguments[0].scrollIntoView();"
    PROPERTIES_XPATH = "//div[@style='position: relative;']"
    BOTTOM_PAGE_XPATH = "//div[@class='G3BoaHW05R4rguvqgn-Oo']"

    @classmethod
    def define_parser(cls):
        """
        Creates the command line arguments
        """
        arg_parser = argparse.ArgumentParser(
            description="Scraping OnMap website | Checkout https://www.onmap.co.il/en/")
        arg_parser.add_argument(
            "property_listing_type",
            choices=Configuration.PROPERTY_LISTING_TYPE,
            help="choose which type of properties you would like to scrape",
            type=str)
        arg_parser.add_argument('--limit', '-l',
                                help="limit to n number of scrolls per page", metavar="n",
                                type=int,
                                required=False)
        arg_parser.add_argument("--print", '-p', help="print the results to the screen", action="store_true")
        arg_parser.add_argument("--save", '-s',
                                help="save the scraped information into a csv file in the same directory",
                                action="store_true")
        arg_parser.add_argument("--database", '-d',
                                help="inserts new information found into the on_map database",
                                action="store_true")
        arg_parser.add_argument("--fetch", '-f',
                                help="fetches more information for each property using Nominatim API",
                                action="store_true")
        arg_parser.add_argument("--verbose", '-v', help="prints messages during the scraper execution",
                                action="store_true")
        cls.args = arg_parser.parse_args()


class Logger:

    @classmethod
    def start_logging(cls):
        cls.logger = logging.getLogger('on_map_scraper')
        cls.logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter("'%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s'")

        # create a file handler and add it to logger
        file_handler = logging.FileHandler('web_scraper.log', mode='a')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        cls.logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(logging.ERROR)
        stream_handler.setFormatter(formatter)
        cls.logger.addHandler(stream_handler)
