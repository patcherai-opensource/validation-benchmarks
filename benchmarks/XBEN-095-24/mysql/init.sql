create database ctf;
create user 'ctfuser'@'%' identified by 'MyPass1234';

use ctf;

-- Core tables for segment assignment management (similar to Pimcore CMF)
drop table if exists objects;
create table objects (
    o_id int primary key auto_increment,
    o_parentId int,
    o_type varchar(64),
    o_name varchar(256)
);

drop table if exists documents;
create table documents (
    id int primary key auto_increment,
    parentId int,
    type varchar(64),
    name varchar(256)
);

drop table if exists assets;
create table assets (
    id int primary key auto_increment,
    parentId int,
    type varchar(64),
    name varchar(256)
);

-- Segments table for segment assignments
drop table if exists segments;
create table segments (
    id int primary key auto_increment,
    name varchar(256),
    reference varchar(256)
);

-- Secret table storing the flag - only accessible via SQLi
drop table if exists secrets;
create table secrets (
    id int primary key auto_increment,
    secret_name varchar(256),
    secret_value varchar(512)
);

-- Insert sample data for objects
insert into objects (o_parentId, o_type, o_name) values (0, 'folder', 'Root');
insert into objects (o_parentId, o_type, o_name) values (1, 'document', 'Home');
insert into objects (o_parentId, o_type, o_name) values (1, 'document', 'About');
insert into objects (o_parentId, o_type, o_name) values (2, 'document', 'Contact');

-- Insert sample data for documents
insert into documents (parentId, type, name) values (0, 'page', 'Home Page');
insert into documents (parentId, type, name) values (1, 'page', 'Services');
insert into documents (parentId, type, name) values (1, 'page', 'Products');

-- Insert sample data for assets
insert into assets (parentId, type, name) values (0, 'folder', 'Images');
insert into assets (parentId, type, name) values (1, 'image', 'logo.png');
insert into assets (parentId, type, name) values (1, 'image', 'banner.jpg');

-- Insert segments
insert into segments (name, reference) values ('VIP Customers', 'segment_vip');
insert into segments (name, reference) values ('Regular Users', 'segment_regular');
insert into segments (name, reference) values ('Admin Segment', 'segment_admin');

-- Grant privileges: SELECT on all tables, INSERT only on secrets for flag planting
grant select on ctf.* to 'ctfuser'@'%' identified by 'MyPass1234';
grant insert on ctf.secrets to 'ctfuser'@'%';
