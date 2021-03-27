import numpy as np
import pymysql
import sys
from config import DBConfig
from config import Logger as Log
from config import Configuration as Cfg
from utils import *


class DataBaseFeeder:
    """
    This class handles the database that stores the information scraped from the website "On Map"
    """
    def __init__(self, df, listing_type, verbose=False):
        """
        :param df: dataframe to have its information saved into the database
        :type df: pd.DataFrame
        :param verbose: if true, it prints relevant information to the user
        :type verbose: bool
        :param verbose: if true, it prints relevant information to the user
        :type verbose: bool
        """
        self.df = df.replace(np.nan, None)
        self.listing_type = listing_type
        self.verbose = verbose

    def _connect_to_server(self):
        """
        Connecting to the data base host server.
        """
        print_database(verbose=self.verbose)
        Log.logger.debug(Log.connect_to_server(self.listing_type, self.verbose))
        try:
            self.connection = pymysql.connect(DBConfig.HOST, DBConfig.USER, DBConfig.PASSWORD, DBConfig.DATABASE)
            self.cursor = self.connection.cursor()
            self.connection.commit()
        except pymysql.err.OperationalError:
            Log.logger.error(Log.error_connect_server)
            sys.exit(1)
        else:
            Log.logger.info(Log.connection_successful)

    def _city_table_feeder(self):
        """
        Adding new unique cities into the cities table.
        """
        for city in self.df[Cfg.CITY_COL].unique():
            try:
                self.cursor.execute(DBConfig.INSERT_CITY_QUERY, city)
                self.connection.commit()
            except pymysql.err.IntegrityError:
                Log.logger.error(Log.insert_city_error(city))

    def _listing_type_table_feeder(self):
        """
        Adding new unique listings into the listings table.
        """
        for listing in self.df[Cfg.LIST_TYPE_COL].unique():
            try:
                self.cursor.execute(DBConfig.INSERT_LISTINGS_QUERY, listing)
                self.connection.commit()
            except pymysql.err.IntegrityError:
                Log.logger.error(Log.insert_city_error(listing))

    def _property_type_table_feeder(self):
        """
        Adding new unique property types into the property_types table.
        """
        for prop in self.df[Cfg.PROP_TYPE_COL].unique():
            try:
                self.cursor.execute(DBConfig.INSERT_PROPERTY_TYPES_QUERY, prop)
                self.connection.commit()
            except pymysql.err.IntegrityError:
                Log.logger.error(Log.insert_city_error(prop))

    def _get_columns_list(self):
        """
        :return: returns relevant columns, in both list and string formats, to feed the properties table.
        :rtype: tuple
        """
        columns = [str(i) for i in self.df.columns.tolist()]
        columns_list = DBConfig.FK_IDS_LIST + columns[DBConfig.PRICE_COLUMN_IDX:]
        columns_list_string = DBConfig.SEPARATOR.join(columns_list)
        return columns_list, columns_list_string

    def _get_ids_values(self, row):
        """
        :return: returns id's values of cities, listings and property_types in order to fee the properties table.
        :rtype: tuple
        """
        self.cursor.execute(DBConfig.GET_LISTING_TYPE_ID_QUERY, tuple(row)[DBConfig.LISTING_TYPE_IDX])
        listings_id = self.cursor.fetchone()[DBConfig.TUPLE_FIRST_ELEMENT_IDX]

        self.cursor.execute(DBConfig.GET_PROPERTY_TYPE_ID_QUERY, tuple(row)[DBConfig.PROPERTY_TYPE_IDX])
        property_type_id = self.cursor.fetchone()[DBConfig.TUPLE_FIRST_ELEMENT_IDX]

        self.cursor.execute(DBConfig.GET_CITY_ID_QUERY, tuple(row)[DBConfig.CITY_IDX])
        city_id = self.cursor.fetchone()[DBConfig.TUPLE_FIRST_ELEMENT_IDX]

        return listings_id, property_type_id, city_id

    @staticmethod
    def _insert_property_query(columns_list_string, columns_list):
        """
        Inserts a new property into the properties table
        ----
        :param columns_list_string: a string with the names of the database columns
        :type columns_list_string: str
        :param columns_list: a list with the names of the database columns
        :type columns_list: list
        """
        return "INSERT IGNORE INTO properties" \
                  " (" + columns_list_string + ") VALUES (" + "%s, " * (len(columns_list) - 1) + "%s)"

    def _properties_table_feeder(self):
        """
        Adding new records into the properties table.
        """
        for i, row in self.df.iterrows():
            listings_id, property_type_id, city_id = self._get_ids_values(row)
            columns_list, columns_list_string = self._get_columns_list()
            values = tuple([listings_id, property_type_id, city_id] +
                           row.values[DBConfig.PRICE_COLUMN_IDX:].tolist())

            sql = self._insert_property_query(columns_list_string, columns_list)

            try:
                values = tuple(
                    [listings_id, property_type_id, city_id] + row.values[DBConfig.TABLE_FEEDER_COLUMN_IDX:].tolist())
                self.cursor.execute(sql, values)
                self.connection.commit()
            except pymysql.err.IntegrityError:
                Log.logger.error(Log.insert_row_error(row))
            else:
                Log.logger.info(Log.commit_successful)

    def _data_base_feeder(self):
        """
        Feeding the data base with the scraped data frame.
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
        Updates the data base with the scraped data frame.
        """
        self._data_base_feeder()
