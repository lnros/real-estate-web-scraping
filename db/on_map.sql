create DATABASE IF NOT EXISTS on_map;

USE on_map;

CREATE TABLE IF NOT EXISTS `property_types` (
  `id` int PRIMARY KEY,
  `property_type` varchar(255) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS `cities` (
  `id` int PRIMARY KEY,
  `city_name` varchar(255) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS `listings` (
  `id` int PRIMARY KEY,
  `listing_type` varchar(255) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS `properties` (
  `id` int PRIMARY KEY,
  `property_type` int NOT NULL,
  `listing_type` int NOT NULL,
  `city` int NOT NULL,
  `address` varchar(255) NOT NULL,
  `price` float NOT NULL,
  `num_of_rooms` int,
  `floor` int,
  `area_m2` int,
  `parking_spots` int,
  FOREIGN KEY (`property_type`) REFERENCES `property_types` (`id`),
  FOREIGN KEY (`listing_type`) REFERENCES `listings` (`id`),
  FOREIGN KEY (`city`) REFERENCES `cities` (`id`)
);
