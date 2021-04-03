DROP DATABASE IF EXISTS brbeky1hybvf32t4ufxz;
CREATE DATABASE IF NOT EXISTS brbeky1hybvf32t4ufxz;

USE brbeky1hybvf32t4ufxz;

create table cities
(
	id int auto_increment
		primary key,
	city_name varchar(50) not null,
	constraint city_name
		unique (city_name)
);

create table listings
(
	id int auto_increment
		primary key,
	listing_type varchar(50) not null,
	constraint listing_type
		unique (listing_type)
);

create table property_types
(
	id int auto_increment
		primary key,
	property_type varchar(50) not null,
	constraint property_type
		unique (property_type)
);

create table properties
(
	id int auto_increment
		primary key,
	listing_id int null,
	property_type_id int null,
	Price float null,
	city_id int null,
	Address varchar(50) null,
	Rooms int null,
	Floor int null,
	Area int null,
	Parking_spots smallint null,
	ConStatus varchar(50) null,
	latitude float null,
	longitude float null,
	city_hebrew varchar(50) null,
	address_hebrew varchar(50) null,
	state_hebrew varchar(50) null,
	constraint unique_new_home
		unique (listing_id, property_type_id, Price, city_id, Address, ConStatus),
	constraint unique_property
		unique (listing_id, property_type_id, Price, city_id, Address, Rooms, Floor, Area, Parking_spots),
	constraint properties_ibfk_1
		foreign key (city_id) references cities (id),
	constraint properties_ibfk_2
		foreign key (listing_id) references listings (id),
	constraint properties_ibfk_3
		foreign key (property_type_id) references property_types (id)
);

