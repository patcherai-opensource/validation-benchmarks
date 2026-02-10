create database ctf;
create user 'ctfuser'@'%' identified by 'MyPass1234';

use ctf;

drop table if exists uuids;
create table uuids (
    id int primary key auto_increment,
    uuid varchar(36) not null,
    itemType varchar(50),
    itemId int,
    instanceIdentifier varchar(255),
    unique key idx_uuid (uuid)
);

insert into uuids (uuid, itemType, itemId, instanceIdentifier) values 
    ('550e8400-e29b-41d4-a716-446655440001', 'document', 101, 'main-instance'),
    ('550e8400-e29b-41d4-a716-446655440002', 'asset', 102, 'storage-node-1'),
    ('550e8400-e29b-41d4-a716-446655440003', 'object', 103, 'cache-layer'),
    ('550e8400-e29b-41d4-a716-446655440004', 'document', 104, 'backup-node'),
    ('550e8400-e29b-41d4-a716-446655440005', 'asset', 105, 'cdn-edge');

drop table if exists admins;
create table admins (
    id int primary key auto_increment,
    username varchar(100) not null,
    password_hash varchar(64) not null,
    unique key idx_username (username)
);

insert into admins (username, password_hash) values 
    ('admin', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f');

drop table if exists secrets;
create table secrets (
    id int primary key auto_increment,
    secret_key varchar(100) not null,
    secret_value varchar(255) not null
);

grant select on uuids to 'ctfuser'@'%';
grant select on admins to 'ctfuser'@'%';
grant select, insert on secrets to 'ctfuser'@'%';
