import argparse
import string


class Configuration:
    """
    Holds the user parameters for the web scraping.
    """

    # class attr
    args = None

    # SCRAPERS TYPES
    SCRAPERS_TYPES = ('soup', 'selenium')

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
    COLUMNS = ['Price[NIS]', 'Property_type', 'City', 'Address', 'Rooms', 'Floor', 'Area[m^2]',
               'Parking_spots']
    COLUMNS_NOT_SELENIUM = ['Date', 'City_name', 'Street_name', 'House_number', 'Bathrooms', 'Rooms', 'Floor',
                            'Area[m^2]',
                            'Parking_spots_aboveground', 'Parking_spots_underground', 'Price[NIS]', 'Property_type']
    SCROLL_PAUSE_TIME = 1
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

    # XPATHS AND SELENIUM COMMANDS
    PRICE_XPATH = "//span[@class='cWr2cxa0k3zKePxbqpw3L']"
    PROP_TYPE_XPATH = "//div[@class='_1bluUEiq7lEDSV1yeF9mjl']"
    CITY_XPATH = "//div[@property='address']"
    ADDRESS_XPATH = "//div[@property='address']"
    NUM_ROOMS_XPATH = "//div[@property='address']"
    FLOOR_XPATH = "//div[@class='yHLZr2apXqwIyhsOGyagJ']"
    SIZE_XPATH = "//div[@class='yHLZr2apXqwIyhsOGyagJ']"
    PARKING_XPATH = "//div[@class='yHLZr2apXqwIyhsOGyagJ']"
    BOTTOM_PAGE_XPATH = "//div[@class='G3BoaHW05R4rguvqgn-Oo']"
    SCROLL_COMMAND = "arguments[0].scrollIntoView();"
    PROPERTIES_XPATH = "//*[@id='propertiesList']/div[2]/div"

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
        arg_parser.add_argument(
            "scraper_type",
            choices=Configuration.SCRAPERS_TYPES,
            help="choose which type of scraper you would like to use",
            type=str)
        arg_parser.add_argument('--limit', '-l',
                                help="limit to n number of properties per region (soup only)", metavar="n",
                                type=int,
                                required=False)
        arg_parser.add_argument("--print", '-p', help="print the results to the screen", action="store_true")
        arg_parser.add_argument("--save", '-s',
                                help="save the scraped information into a csv file in the same directory",
                                action="store_true")
        arg_parser.add_argument("--verbose", '-v', help="prints messages during the scraper execution",
                                action="store_true")
        cls.args = arg_parser.parse_args()
