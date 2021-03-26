import argparse
import logging
import string
import sys

COMMIT_TO_DB_SUCCESSFUL = "_save_to_data_base: Commit to db successful"

DB_SUCCESSFUL = "f_save_to_data_base: Connection to the db successful"

ERROR_CONNECTION = f"failed to connect to the server."

QUITTING_DRIVER = "main: Quitting driver"

CLOSING_DRIVER = "main: Closing driver"

SCRAPER_OBJECT = "main: Creating the scraper object"

NO_URLS_FOUND_TO_SCRAPE = 'main: No urls found to scrape.'

PARSER_WAS_SUCCESSFUL = 'main: CLI parser was successful.'

FINISHED_SUCCESSFULLY_FETCH = "fetch_more_attributes: finished successfully"

GEOFETCHER_INITIALIZED = "fetch_more_attributes: geofetcher initialized"

MORE_ATTRIBUTES_STARTING = "fetch_more_attributes: starting"

NEW_HOMES_FINISHED = "_scroll_new_homes: finished"

SCROLL_FINISHED = "_scroll: finished"

HOMES_FINISHED_SCROLLING = "_scroll_new_homes: finished scrolling"

FINISHED_SCROLLING = "_scroll: finished scrolling"


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
    INSERT_CITY_QUERY = "INSERT IGNORE INTO cities(city_name) values (%s)"
    INSERT_LISTINGS_QUERY = "INSERT IGNORE INTO listings(listing_type) values (%s)"
    INSERT_PROPERTY_TYPES_QUERY = "INSERT IGNORE INTO property_types(property_type) values (%s)"

    FK_IDS_LIST = ['listing_id', 'property_type_id', 'city_id']
    PRICE_COLUMN_IDX = 3
    LATITUDE_COLUMN_IDX = -5

    GET_LISTING_TYPE_ID_QUERY = "SELECT id FROM listings WHERE listing_type = %s"
    GET_PROPERTY_TYPE_ID_QUERY = "SELECT id FROM property_types WHERE property_type = %s"
    GET_CITY_ID_QUERY = "SELECT id FROM cities WHERE city_name = %s"

    TUPLE_FIRST_ELEMENT_IDX = 0

    LISTING_TYPE_IDX = 0
    PROPERTY_TYPE_IDX = 1
    CITY_IDX = 2

    SEPARATOR = ","
    TABLE_FEEDER_COLUMN_IDX = 3


class Configuration:
    """
    Holds the user parameters for the web scraping.
    """

    # class attr
    args = None

    # PARAMETERS KWARGS KEYS
    VERBOSE_KEY = 'verbose'
    LIMIT_KEY = 'limit'
    PRINT_KEY = 'to_print'
    SAVE_KEY = 'save'
    DB_KEY = 'to_database'
    FETCH_KEY = 'fetch_info'
    LISTING_TYPE_KEY = 'listing_type'

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
    DICT_PROPERTY_ID = {'id': 'propertiesList'}
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
    PROPERTIES_LIST_IDX = 1
    LEN_PROPER = 2

    # XPATHS AND SELENIUM COMMANDS
    SCROLL_COMMAND = "arguments[0].scrollIntoView();"
    PROPERTIES_XPATH = "//div[@style='position: relative;']"
    BOTTOM_PAGE_XPATH = "//div[@class='G3BoaHW05R4rguvqgn-Oo']"

    # Handling strings
    ENCODING = "ISO-8859-8"
    COMMERCIAL_FILENAME = "commercial.csv"
    NEW_HOMES_FILENAME = "new_homes.csv"
    PROJECT = 'project'
    COMMERCIAL = 'commercial'

    # DF columns names
    PRICE_COL = 'Price'
    ROOM_COL = 'Rooms'
    FLOOR_COL = 'Floor'
    AREA_COL = 'Area'
    CITY_COL = 'City'
    PARKING_COL = 'Parking_spots'
    PROP_TYPE_COL = 'Property_type'
    LIST_TYPE_COL = 'listing_type'

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
    """
    This class handles logging for the entire web scraping process
    """
    logger = None
    scroll_finished = FINISHED_SCROLLING
    scroll_finished_new_home = HOMES_FINISHED_SCROLLING
    end_scroll_function = SCROLL_FINISHED
    end_scroll_new_home = NEW_HOMES_FINISHED
    fetch_more_init = MORE_ATTRIBUTES_STARTING
    geofetcher_init = GEOFETCHER_INITIALIZED
    end_fetch_more_att = FINISHED_SUCCESSFULLY_FETCH
    main_cli = PARSER_WAS_SUCCESSFUL
    main_no_url = NO_URLS_FOUND_TO_SCRAPE
    main_scrape_obj = SCRAPER_OBJECT
    main_closing_driver = CLOSING_DRIVER
    main_quit_drive = QUITTING_DRIVER
    error_connect_server = ERROR_CONNECTION
    connection_successful = DB_SUCCESSFUL
    commit_successful = COMMIT_TO_DB_SUCCESSFUL

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

    @staticmethod
    def scroll_error(ele_to_scroll):
        """
        Message for the logger in case of error when scrolling.
        ----
        :param ele_to_scroll: html element to look for when scrolling
        :type ele_to_scroll: str
        :return: error message
        :rtype: str
        """
        return f"_scroll: ele_to_scroll should have a content but it is {ele_to_scroll}"

    @staticmethod
    def scroll_new_homes(prev_len):
        """
        Message for the logger in when scrolling.
        ----
        :param prev_len: number of elements found when scrolling
        :type prev_len: int
        :return: message
        :rtype: str
        """
        return f"_scroll_new_homes:prev_len {prev_len}"

    @staticmethod
    def end_save_csv(url):
        """
        Message for the logger when finished saving an url content to a csv
        ----
        :param url: url address
        :type url: int
        :return: message
        :rtype: str
        """
        return f"_save_to_csv: finished {url}"

    @staticmethod
    def init_print_save_df(url, to_print, save, to_database, verbose, listing_type):
        """
        Message for the logger at beginning of print_save_df function
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
        return f"_print_save_df: Checking if print {url}, to_print={to_print}, save={save}, to_database={to_database}, " \
               f"verbose={verbose}, listing_type={listing_type}"

    @staticmethod
    def saving_print_save_df(url, to_print, save, to_database, verbose, listing_type):
        """
        Message for the logger before saving to a csv in print_save_df function
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
        return f"_print_save_df: Saving into csv {url}, to_print={to_print}, save={save}, to_database={to_database}, " \
               f"verbose={verbose}, listing_type={listing_type}"

    @staticmethod
    def db_print_save_df(url, to_print, save, to_database, verbose, listing_type):
        """
        Message for the logger before saving into the db in print_save_df function
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
        return f"_print_save_df: Saving into db {url}, to_print={to_print}, save={save}, to_database={to_database}, " \
               f"verbose={verbose}, listing_type={listing_type}"

    @staticmethod
    def end_print_save(url):
        """
        Message for the logger when finished running the function _print_save_df
        ----
        :param url: url address
        :type url: int
        :return: message
        :rtype: str
        """
        return f"_print_to_save: finished {url}"

    @staticmethod
    def pulling_row_info(row_number):
        """
        Message for the logger when pulling row information in fetch_more_attributes function
        ----
        :param row_number: row number in the dataframe
        :type row_number: int
        :return: message
        :rtype: str
        """
        return f"fetch_more_attributes: Pulling info for row {row_number}"

    @staticmethod
    def exception_fetch_more_attributes(row_number, exception):
        """
        Message for the logger when an exception occurred when pulling row information in fetch_more_attributes function
        ----
        :param row_number: row number in the dataframe
        :type row_number: int
        :param exception: error message
        :type exception: exception
        :return: message
        :rtype: str
        """
        return f"fetch_more_attributes: row {row_number}, {exception}"

    @staticmethod
    def not_fetched(fetch_info):
        """
        Message for the logger when additional information was not fetched
        ----
        :param fetch_info: row number in the dataframe
        :type fetch_info: bool
        :return: message
        :rtype: str
        """
        return f"fetch_more_attributes: fetch info == {fetch_info}"

    @staticmethod
    def creating_df(url):
        """
        Message for the logger when _create_df is called
        ----
        :param url: url address
        :type url: str
        :return: message
        :rtype: str
        """
        return f"create_df: Creating dataframe from {url}"

    @staticmethod
    def created_df(url):
        """
        Message for the logger when _create_df is finished
        ----
        :param url: url address
        :type url: str
        :return: message
        :rtype: str
        """
        return f"create_df: Created dataframe from {url} successfully"

    @staticmethod
    def scraping(url):
        """
        Message for the logger when scrap_url is called
        ----
        :param url: url address
        :type url: str
        :return: message
        :rtype: str
        """
        return f"scrap_url: Scrolling {url}"

    @staticmethod
    def before_scroll(url):
        """
        Message for the logger before _scroll is called
        ----
        :param url: url address
        :type url: str
        :return: message
        :rtype: str
        """
        return f"scrap_url: Scrolling {url} - not new_homes"

    @staticmethod
    def before_scroll_new_home(url):
        """
        Message for the logger before _scroll_new_homes is called
        ----
        :param url: url address
        :type url: str
        :return: message
        :rtype: str
        """
        return f"scrap_url: Scrolling {url} - new_homes"

    @staticmethod
    def before_scraping(url):
        """
        Message for the logger before starting to actually scrape in scrap_url
        ----
        :param url: url address
        :type url: str
        :return: message
        :rtype: str
        """
        return f"scrap_url: Scraping {url}"

    @staticmethod
    def finished_scraping(url):
        """
        Message for the logger at the end of scrap_url
        ----
        :param url: url address
        :type url: str
        :return: message
        :rtype: str
        """
        return f"scrap_url: finished {url}"

    @staticmethod
    def main_scraping(url):
        """
        Message for the logger before calling scrap_url
        ----
        :param url: url address
        :type url: str
        :return: message
        :rtype: str
        """
        return f"main: Scraping {url}"

    @staticmethod
    def main_scraped_success(url):
        """
        Message for the logger after all scraping operations are done for the particular url
        ----
        :param url: url address
        :type url: str
        :return: message
        :rtype: str
        """
        return f"main: Scrapped {url} successfully"

    @staticmethod
    def connect_to_server(listing, verbose):
        """
        Message for the logger before connecting to db server
        ----
        :param listing: listing type of the dataframe
        :type listing: str
        :param verbose: whether nor not to print relevant info to the user
        :type verbose: bool
        :return: message
        :rtype: str
        """
        return f"_save_to_data_base: Connecting to the db listing_type={listing}, verbose={verbose}"

    @staticmethod
    def insert_city_error(city):
        """
        Message for the logger when error for inserting existing city in cities table
        ----
        :param city: city already in table
        :type city: str
        :return: message
        :rtype: str
        """
        return f"_save_to_data_base: {city} is already in cities."

    @staticmethod
    def insert_city_error(listing):
        """
        Message for the logger when error for inserting existing listing type in listings table
        ----
        :param listing: listing already in table
        :type listing: str
        :return: message
        :rtype: str
        """
        return f"_save_to_data_base: {listing} is already in listings."

    @staticmethod
    def insert_city_error(property):
        """
        Message for the logger when error for inserting existing property in properties table
        ----
        :param property: property already in table
        :type property: str
        :return: message
        :rtype: str
        """
        return f"_save_to_data_base: {property} is already in properties."

    @staticmethod
    def insert_row_error(row):
        """
        Message for the logger when error for inserting existing property in properties table
        ----
        :param row: row already in table
        :type row: pd.Series
        :return: message
        :rtype: str
        """
        return f"_save_to_data_base: {row} is already in properties. "

