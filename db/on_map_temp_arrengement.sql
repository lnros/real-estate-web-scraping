DROP DATABASE IF EXISTS brbeky1hybvf32t4ufxz;
CREATE DATABASE IF NOT EXISTS brbeky1hybvf32t4ufxz;

use brbeky1hybvf32t4ufxz;

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
	id INT AUTO_INCREMENT
		PRIMARY KEY,
	listing_id int,
	property_type_id int,
	Price FLOAT NULL,
	city_id INT,
	Address VARCHAR(50) NULL,
	Rooms INT NULL,
	Floor INT NULL,
	Area INT NULL,
	Parking_spots SMALLINT NULL,
	ConStatus VARCHAR(50) NULL,
    latitude INT NULL,
    longitude INT NULL,
    city_hebrew VARCHAR(50) NULL,
    address_hebrew VARCHAR(50) NULL,
    state_hebrew VARCHAR(50) NULL,

	CONSTRAINT properties_ibfk_1
		FOREIGN KEY (city_id) REFERENCES cities (id),

	CONSTRAINT properties_ibfk_2
	FOREIGN KEY (listing_id) REFERENCES listings (id),

	CONSTRAINT properties_ibfk_3
	FOREIGN KEY (property_type_id) REFERENCES property_types (id)
);

ALTER TABLE properties ADD UNIQUE unique_property (listing_id, property_type_id, Price, city_id , Address, Rooms, Floor, Area, Parking_spots);
ALTER TABLE properties ADD UNIQUE unique_new_home (listing_id, property_type_id, Price, city_id , Address, ConStatus);


CREATE INDEX City
	ON properties city_id);

CREATE INDEX listing_type
	ON properties (listing_id);

CREATE INDEX property_type
	ON properties (property_type_id);