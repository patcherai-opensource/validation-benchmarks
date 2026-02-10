create database ctf;
create user 'ctfuser'@'%' identified by 'MyPass1234';


use ctf;

-- UUID table similar to Pimcore's Tool\UUID structure
drop table if exists uuids;
create table uuids (
    id int primary key auto_increment,
    uuid varchar(36) NOT NULL,
    itemId int,
    type varchar(256),
    instanceIdentifier varchar(256),
    data text
);

-- Sample UUIDs representing various system objects
insert into uuids (uuid, itemId, type, instanceIdentifier, data) values 
    ("550e8400-e29b-41d4-a716-446655440000", 1, "document", "portal", "Homepage document"),
    ("6ba7b810-9dad-11d1-80b4-00c04fd430c8", 2, "asset", "media", "Logo image"),
    ("6ba7b811-9dad-11d1-80b4-00c04fd430c9", 3, "object", "products", "Product catalog");

-- Secrets table storing sensitive information (the flag)
drop table if exists secrets;
create table secrets (
    id int primary key auto_increment,
    secret_key varchar(256),
    secret_value text
);

-- The flag will be inserted via build arg substitution
-- Placeholder for the flag - will be replaced during build

grant select on uuids to 'ctfuser'@'%' identified by 'MyPass1234';
grant select on secrets to 'ctfuser'@'%' identified by 'MyPass1234';
