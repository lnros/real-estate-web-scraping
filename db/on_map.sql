drop DATABASE IF EXISTS on_map;
create DATABASE IF NOT EXISTS on_map;

USE on_map;

CREATE TABLE IF NOT EXISTS `property_types` (
  `id` int NOT NULL auto_increment,
  `property_type` varchar(50) UNIQUE NOT NULL,
   PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS `cities` (
  `id` int NOT NULL auto_increment,
  `city_name` varchar(50) UNIQUE NOT NULL,
  PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS `listings` (
  `id`  int NOT NULL auto_increment,
  `listing_type` varchar(50) UNIQUE NOT NULL,
   PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS `properties` (
  `id` bigint NOT NULL auto_increment,
  `listing_type` varchar(100),
  `property_type` varchar(100) ,
  `Price` float ,
  `City` varchar(50) ,
  `Address` varchar(50),
  `Rooms` int,
  `Floor` int,
  `Area` int,
  `Parking_spots` smallint,
  PRIMARY KEY (id),
  FOREIGN KEY (`property_type`) REFERENCES `property_types` (`property_type`),
  FOREIGN KEY (`listing_type`) REFERENCES `listings` (`listing_type`),
  FOREIGN KEY (`city`) REFERENCES `cities` (`city_name`)
);

CREATE TABLE IF NOT EXISTS `new_homes` (
  `id` bigint NOT NULL auto_increment,
  `listing_type` varchar(100),
  `price` float,
  `city` varchar(50),
  `address` varchar(50),
  `Status` varchar(50),
  PRIMARY KEY (id),
  FOREIGN KEY (`listing_type`) REFERENCES `listings` (`listing_type`),
  FOREIGN KEY (`city`) REFERENCES `cities` (`city_name`)
);