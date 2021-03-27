from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim
from geopy.adapters import AioHTTPAdapter

from config import GeoFetcherConfig as Cfg


class GeoFetcher:
    """
    Based on Geopy, uses Nominatim service to retrieve more information of a property given its row in a dataframe
    """

    def __init__(self):
        # Not in use since we are working asynchronously
        self._geolocator = Nominatim(user_agent=Cfg.USER_AGENT)
        self.geocode = RateLimiter(self._geolocator.geocode, min_delay_seconds=Cfg.DELAY_TIME)

    async def pull_row_info(self, row):
        """
        Pulls from Nominatim the additional information wanted and add it to the property row from a dataframe.
        It performs the requests asynchronously.
        ----
        :param row: a row from the properties dataframe
        :type row: pd.Series
        :return: the same row but with the information retrieved from Nominatim
        :rtype: pd.Series
        """

        full_address = row[Cfg.ROW_ADDRESS_KEY] + Cfg.WHITESPACE + row[Cfg.ROW_CITY_KEY]
        async with Nominatim(user_agent=Cfg.USER_AGENT, adapter_factory=AioHTTPAdapter) as geolocator:
            location = await geolocator.geocode(full_address, addressdetails=True)
        row[Cfg.LAT_KEY] = self._fetch_latitude(location)
        row[Cfg.LON_KEY] = self._fetch_longitude(location)
        row[Cfg.CITY_HEBREW_KEY] = self._fetch_city_hebrew(location)
        row[Cfg.ADDRESS_HEBREW_KEY] = self._fetch_road_hebrew(location)
        row[Cfg.STATE_HEBREW_KEY] = self._fetch_state_hebrew(location)
        return row

    @staticmethod
    def _fetch_latitude(location):
        """
        Based on the address previously retrieved, it fetches its latitude
        ----
        :param location: information retrieved from Nominatim using geopy
        :type location: a geopy geocode object
        :return: latitude
        :rtype: float
        """
        try:
            return location.latitude
        except AttributeError:
            return None

    @staticmethod
    def _fetch_longitude(location):
        """
        Based on the address previously retrieved, it fetches its longitude
        ----
        :param location: information retrieved from Nominatim using geopy
        :type location: a geopy geocode object
        :return: longitude
        :rtype: float
        """
        try:
            return location.longitude
        except AttributeError:
            return None

    @staticmethod
    def _fetch_city_hebrew(location):
        """
        Based on the address previously retrieved, it fetches the Hebrew name from the city
        ----
        :param location: information retrieved from Nominatim using geopy
        :type location: a geopy geocode object
        :return: city name in Hebrew
        :rtype: str
        """
        try:
            return location.raw[Cfg.ADDRESS_KEY][Cfg.CITY_KEY]
        except AttributeError:
            return None
        except KeyError:
            return None

    @staticmethod
    def _fetch_road_hebrew(location):
        """
        Based on the address previously retrieved, it fetches the road name in Hebrew
        ----
        :param location: information retrieved from Nominatim using geopy
        :type location: a geopy geocode object
        :return: road name in Hebrew
        :rtype: str
        """
        try:
            return location.raw[Cfg.ADDRESS_KEY][Cfg.ROAD_KEY]
        except AttributeError:
            return None
        except KeyError:
            return None

    @staticmethod
    def _fetch_state_hebrew(location):
        """
        Based on the address previously retrieved, it fetches the state (מחוז) name in Hebrew
        ----
        :param location: information retrieved from Nominatim using geopy
        :type location: a geopy geocode object
        :return: state name in Hebrew (מחוז)
        :rtype: str
        """
        try:
            return location.raw[Cfg.ADDRESS_KEY][Cfg.STATE_KEY]
        except AttributeError:
            return None
        except KeyError:
            return None
