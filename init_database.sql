create database LaunchBooking;
use LaunchBooking;

create table RestaurantInformation (
	id INT AUTO_INCREMENT
	,name varchar(50)
	,primary key (id)
	);

create table RestaurantMenu (	
	id INT AUTO_INCREMENT
	,name varchar(50)
	,primary key (id)
	);

create table User (
	id INT AUTO_INCREMENT
	,user_name varchar(50)
	,password varchar(50)
	,primary key (id)
	);

create table BookingInformation (
	id INT AUTO_INCREMENT
	,name varchar(50)
	,primary key (id)
	);
