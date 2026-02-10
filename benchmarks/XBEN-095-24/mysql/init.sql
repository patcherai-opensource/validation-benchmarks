create database ctf;
create user 'ctfuser'@'%' identified by 'MyPass1234';

use ctf;

drop table if exists users;
create table users (
    id int primary key auto_increment,
    username varchar(256),
    password varchar(256),
    role varchar(64)
);

insert into users (username, password, role) values ("admin", "admin123", "administrator"); 

drop table if exists customers;
create table customers (
    id int primary key auto_increment,
    parentId int,
    name varchar(256),
    email varchar(256),
    segment_id int
);

insert into customers (parentId, name, email, segment_id) values 
    (0, "John Smith", "john@example.com", 1),
    (0, "Jane Doe", "jane@example.com", 2),
    (1, "Bob Wilson", "bob@example.com", 3);

drop table if exists objects;
create table objects (
    o_id int primary key auto_increment,
    o_parentId int,
    o_name varchar(256),
    o_type varchar(64)
);

insert into objects (o_parentId, o_name, o_type) values 
    (0, "Root Object", "container"),
    (1, "Child Object 1", "item"),
    (1, "Child Object 2", "item");

drop table if exists documents;
create table documents (
    id int primary key auto_increment,
    parentId int,
    title varchar(256),
    content text
);

insert into documents (parentId, title, content) values 
    (0, "Welcome Document", "Welcome to the Customer Management Framework"),
    (1, "User Guide", "This is the user guide...");

drop table if exists assets;
create table assets (
    id int primary key auto_increment,
    parentId int,
    filename varchar(256),
    filepath varchar(512)
);

insert into assets (parentId, filename, filepath) values 
    (0, "logo.png", "/assets/images/logo.png"),
    (0, "config.json", "/assets/config/config.json");

drop table if exists system_config;
create table system_config (
    id int primary key auto_increment,
    config_key varchar(128),
    config_value text
);

grant select on ctf.* to 'ctfuser'@'%' identified by 'MyPass1234';
