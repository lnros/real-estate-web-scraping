DROP DATABASE IF EXISTS on_map;
CREATE DATABASE IF NOT EXISTS on_map;

USE on_map;

CREATE TABLE cities
(
	id INT AUTO_INCREMENT
		PRIMARY KEY,
	city_name VARCHAR(50) NOT NULL ,
	CONSTRAINT city_name
		UNIQUE (city_name)
);

CREATE TABLE listings
(
	id INT AUTO_INCREMENT
		PRIMARY KEY,
	listing_type VARCHAR(50) NOT NULL,
	CONSTRAINT listing_type
		UNIQUE (listing_type)
);

CREATE TABLE new_homes
(
	id VARCHAR(40) NOT NULL,
	listing_type VARCHAR(100) NULL,
	price FLOAT NULL,
	city VARCHAR(50) NULL,
	address VARCHAR(50) NULL,
	Status VARCHAR(50) NULL,
	CONSTRAINT new_homes_id_uindex
		UNIQUE (id),
	CONSTRAINT new_homes_ibfk_1
		FOREIGN KEY (listing_type) REFERENCES listings (listing_type),
	CONSTRAINT new_homes_ibfk_2
		FOREIGN KEY (city) REFERENCES cities (city_name)
);

CREATE INDEX city
	ON new_homes (city);

CREATE INDEX listing_type
	ON new_homes (listing_type);

ALTER TABLE new_homes
	ADD PRIMARY KEY (id);

CREATE TABLE property_types
(
	id INT AUTO_INCREMENT
		PRIMARY KEY,
	property_type VARCHAR(50) NOT NULL,
	CONSTRAINT property_type
		UNIQUE (property_type)
);

CREATE TABLE properties
(
	id VARCHAR(40) NOT NULL,
	listing_type VARCHAR(100) NULL ,
	property_type VARCHAR(100) NULL ,
	Price FLOAT NULL,
	City VARCHAR(50) NULL ,
	Address VARCHAR(50) NULL ,
	Rooms INT NULL,
	Floor INT NULL,
	Area INT NULL,
	Parking_spots SMALLINT NULL,
	CONSTRAINT properties_id_uindex
		UNIQUE (id),
	CONSTRAINT properties_ibfk_1
		FOREIGN KEY (property_type) REFERENCES property_types (property_type),
	CONSTRAINT properties_ibfk_2
		FOREIGN KEY (listing_type) REFERENCES listings (listing_type),
	CONSTRAINT properties_ibfk_3
		FOREIGN KEY (City) REFERENCES cities (city_name)
);

CREATE INDEX City
	ON properties (City);

CREATE INDEX listing_type
	ON properties (listing_type);

CREATE INDEX property_type
	ON properties (property_type);

ALTER TABLE properties
	ADD PRIMARY KEY (id);

