import sys
import numpy as np
import pymysql
from config import DBConfig
from config import Configuration as Cfg
from config import Logger as Log
from utils import *

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


class DataBaeFeeder:

    def __init__(self, df, listing_type, verbose=False):
        self.df = df.replace(np.nan, None)
        self.listing_type = listing_type
        self.verbose = verbose

    def _connect_to_server(self):
        """
        connecting to the data base host server.
        """
        print_database(verbose=self.verbose)
        Log.logger.debug(f"_connect_to_server: Connecting to the db"
                         f" listing_type={self.listing_type}, verbose={self.verbose}")
        try:
            self.connection = pymysql.connect(DBConfig.HOST, DBConfig.USER, DBConfig.PASSWORD, DBConfig.DATABASE)
            self.cursor = self.connection.cursor()
            self.connection.commit()
        except pymysql.err.OperationalError:
            Log.logger.error(f"_connect_to_server: failed to connect to the server: {DBConfig.HOST}. ")
            sys.exit(1)
        else:
            Log.logger.info("f_connect_to_server: Connection to the db successful")

    def _city_table_feeder(self):
        """
        adding new unique cities into the cities table.
        """
        for city in self.df['City'].unique():
            try:
                self.cursor.execute(INSERT_CITY_QUERY, city)
                self.connection.commit()
            except pymysql.err.IntegrityError:
                Log.logger.error(f"_city_table_feeder: {city} is already in cities. ")

    def _listing_type_table_feeder(self):
        """
        adding new unique listings into the listings table.
        """
        for listing in self.df['listing_type'].unique():
            try:
                self.cursor.execute(INSERT_LISTINGS_QUERY, listing)
                self.connection.commit()
            except pymysql.err.IntegrityError:
                Log.logger.error(f"_listing_type_table_feeder: {listing} is already in listings. ")

    def _property_type_table_feeder(self):
        """
        adding new unique property types into the property_types table.
        """
        for prop in self.df['Property_type'].unique():
            try:
                self.cursor.execute(INSERT_PROPERTY_TYPES_QUERY, prop)
                self.connection.commit()
            except pymysql.err.IntegrityError:
                Log.logger.error(f"_property_type_table_feeder: {prop} is already in property_types. ")

    def _get_columns_list(self):
        """
        returns relevant columns, in both list and string formats, to feed the properties table.
        """
        columns = [str(i) for i in self.df.columns.tolist()]
        columns_list = FK_IDS_LIST + columns[PRICE_COLUMN_IDX:]
        columns_list_string = Cfg.SEPARATOR.join(columns_list)
        return columns_list, columns_list_string

    def _get_ids_values(self, row):
        """
        returns id's values of cities, listings and property_types in order to fee the properties table.
        """
        self.cursor.execute(GET_LISTING_TYPE_ID_QUERY, tuple(row)[LISTING_TYPE_IDX])
        listings_id = self.cursor.fetchone()[TUPLE_FIRST_ELEMENT_IDX]

        self.cursor.execute(GET_PROPERTY_TYPE_ID_QUERY, tuple(row)[PROPERTY_TYPE_IDX])
        property_type_id = self.cursor.fetchone()[TUPLE_FIRST_ELEMENT_IDX]

        self.cursor.execute(GET_CITY_ID_QUERY, tuple(row)[CITY_IDX])
        city_id = self.cursor.fetchone()[TUPLE_FIRST_ELEMENT_IDX]

        return listings_id, property_type_id, city_id

    def _properties_table_feeder(self):
        """
        adding new records into the properties table.
        """
        for i, row in self.df.iterrows():
            listings_id, property_type_id, city_id = self._get_ids_values(row)
            columns_list, columns_list_string = self._get_columns_list()
            values = tuple([listings_id, property_type_id, city_id] +
                           row.values[PRICE_COLUMN_IDX:].tolist())

            sql = "INSERT IGNORE INTO properties" \
                  " (" + columns_list_string + ") VALUES (" + "%s, " * (len(columns_list) - 1) + "%s)"

            try:
                values = tuple([listings_id, property_type_id, city_id] + row.values[PRICE_COLUMN_IDX:].tolist())
                self.cursor.execute(sql, values)
                self.connection.commit()
            except pymysql.err.IntegrityError:
                Log.logger.error(f"_properties_table_feeder: {row} is already in properties. ")
            else:
                Log.logger.info("_properties_table_feeder: Commit to db successful")

    def _data_base_feeder(self):
        """
        feeding the data base with the scraped data frame.
        First feeding cities, listings and property_types tables.
        Second, feeding the properties table which have foreign keys constraints
        with cities, listings and property_types tables.
        """
        self._connect_to_server()
        self._city_table_feeder()
        self._listing_type_table_feeder()
        self._property_type_table_feeder()
        self._properties_table_feeder()

    def update_db(self):
        """
        updates the data base with the scraped data frame.
        """
        self._data_base_feeder()
