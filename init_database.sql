create database launch_booking CHARACTER SET 'utf8' COLLATE 'utf8_general_ci';
use launch_booking;


create table restaurant_info(
	id INT AUTO_INCREMENT
	,name VARCHAR(50) UNIQUE NOT NULL
	,phone TEXT NOT NULL
	,note TEXT 
	,primary key (id)
	)ENGINE=InnoDB DEFAULT CHARSET=utf8;
	
insert into restaurant_info (id,name, phone,note)  values (1,'万家肠粉', '111222333444','hehe');
insert into restaurant_info (id,name, phone,note)  values (2,'石磨坊', '110,112','hehe');
	
create table dish_info (	
	id INT AUTO_INCREMENT
	,restaurant_id INT NOT NULL #restaurant_info.id
	,dish_name TEXT NOT NULL
	,price FLOAT NOT NULL
	,note TEXT 
	,primary key (id)
	)ENGINE=InnoDB DEFAULT CHARSET=utf8;

insert into dish_info (restaurant_id, dish_name, price)  values (1,'牛腩饭',16); 
insert into dish_info (restaurant_id, dish_name, price)  values (1,'猪脚饭',16); 
insert into dish_info (restaurant_id, dish_name, price)  values (1,'基友饭',16); 

insert into dish_info (restaurant_id, dish_name, price)  values (2,'牛腩饭',16); 
insert into dish_info (restaurant_id, dish_name, price)  values (2,'猪脚饭',16); 
insert into dish_info (restaurant_id, dish_name, price)  values (2,'基友饭',16); 

	
create table user_info (
	id INT AUTO_INCREMENT
	,user_name VARCHAR(50) UNIQUE
	,password TEXT NOT NULL
	,privilege INT
	,balance FLOAT
	,primary key (id)
	)ENGINE=InnoDB DEFAULT CHARSET=utf8;

insert into user_info (user_name, password, privilege, balance)  values ('ay', '202CB962AC59075B964B07152D234B70', 1, 0);
insert into user_info (user_name, password, privilege, balance)  values ('ay1', '202CB962AC59075B964B07152D234B70', 0, 0);
insert into user_info (user_name, password, privilege, balance)  values ('ay2', '202CB962AC59075B964B07152D234B70', 0, 0);
	
create table booking_info (
	id INT AUTO_INCREMENT
	,dish_id INT
	,user_id INT
	,booking_time DATETIME
	,payment FLOAT
	,status INT DEFAULT '0' # 0 means the booking action is pending, 1 means the booking action has committed
	,primary key (id)
	)ENGINE=InnoDB DEFAULT CHARSET=utf8;
	
create table topup_info(
	id INT AUTO_INCREMENT
	,user_id INT
	,payment FLOAT
	,topup_time DATETIME	
	,primary key (id)
	) ENGINE=InnoDB DEFAULT CHARSET=utf8;

create table transaction_journal(
	id INT AUTO_INCREMENT
	,transaction_type INT
	,associate_id INT  #if transaction_type is 0, it is topup_info.id. if transaction_type is 1, it is booking_info.id
	,user_id INT
	,transaction_amount FLOAT
	,transaction_time DATETIME
	,primary key (id)
	)ENGINE=InnoDB DEFAULT CHARSET=utf8;
	
alter database launch_booking  character set utf8;
	
	

	
	
	
	
	
	
	
	
	
	
