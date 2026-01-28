create database ctf;
create user 'ctfuser'@'%' identified by 'MyPass1234';

use ctf;

-- Assets table for UUID-based lookups
drop table if exists assets;
create table assets (
    id int primary key auto_increment,
    uuid varchar(36) not null,
    asset_name varchar(256),
    asset_type varchar(64),
    status varchar(32) default 'public',
    secret_data text
);

-- Public assets (visible in asset browser)
insert into assets (uuid, asset_name, asset_type, status, secret_data) values 
    ('550e8400-e29b-41d4-a716-446655440001', 'Company Logo', 'image', 'public', null),
    ('550e8400-e29b-41d4-a716-446655440002', 'Product Catalog', 'document', 'public', null),
    ('550e8400-e29b-41d4-a716-446655440003', 'Marketing Video', 'video', 'public', null),
    ('550e8400-e29b-41d4-a716-446655440004', 'Brand Guidelines', 'document', 'public', null);

-- System configuration table (contains the flag)
drop table if exists system_config;
create table system_config (
    id int primary key auto_increment,
    config_key varchar(128) not null,
    config_value text
);

insert into system_config (config_key, config_value) values
    ('app_name', 'AssetCore'),
    ('version', '2.4.1'),
    ('maintenance_mode', 'false'),
    ('admin_secret', 'PLACEHOLDER_FLAG');

-- Users table for admin panel (decoy)
drop table if exists users;
create table users (
    id int primary key auto_increment,
    username varchar(256),
    password_hash varchar(256),
    role varchar(32)
);

insert into users (username, password_hash, role) values 
    ('admin', 'e10adc3949ba59abbe56e057f20f883e', 'administrator'),
    ('viewer', '098f6bcd4621d373cade4e832627b4f6', 'readonly');

grant select on ctf.* to 'ctfuser'@'%' identified by 'MyPass1234';
