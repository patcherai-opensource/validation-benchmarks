create database ctf;
create user 'ctfuser'@'%' identified by 'MyPass1234';

use ctf;

-- Assets table (similar to Pimcore's UUID table structure)
drop table if exists assets;
create table assets (
    id int primary key auto_increment,
    uuid varchar(36) not null,
    name varchar(256),
    type varchar(64),
    path varchar(512),
    is_public tinyint(1) default 0,
    created_at timestamp default current_timestamp,
    unique key (uuid)
);

-- System secrets table (contains the flag)
drop table if exists system_secrets;
create table system_secrets (
    id int primary key auto_increment,
    secret_key varchar(128),
    secret_value text,
    created_at timestamp default current_timestamp
);

-- Insert sample public assets
insert into assets (uuid, name, type, path, is_public) values 
    ('550e8400-e29b-41d4-a716-446655440001', 'company_logo.png', 'image', '/assets/images/logo.png', 1),
    ('550e8400-e29b-41d4-a716-446655440002', 'product_catalog.pdf', 'document', '/assets/docs/catalog.pdf', 1),
    ('550e8400-e29b-41d4-a716-446655440003', 'homepage_banner.jpg', 'image', '/assets/images/banner.jpg', 1);

-- Insert private/internal assets
insert into assets (uuid, name, type, path, is_public) values 
    ('a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'internal_config.json', 'config', '/private/config.json', 0),
    ('f9e8d7c6-b5a4-3210-fedc-ba9876543210', 'api_credentials.enc', 'secret', '/private/creds.enc', 0);

-- The flag is stored as a system secret (only accessible via SQL injection)
insert into system_secrets (secret_key, secret_value) values 
    ('database_version', '3.2.1'),
    ('system_flag', 'PLACEHOLDER_FLAG');

grant select on assets to 'ctfuser'@'%';
grant select on system_secrets to 'ctfuser'@'%';
