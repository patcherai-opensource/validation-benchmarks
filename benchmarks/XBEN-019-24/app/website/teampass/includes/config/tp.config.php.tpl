<?php
// TeamPass Configuration File
// Generated during installation

return array(
    'server' => '127.0.0.1',
    'user' => 'teampass_user',
    'pass' => 'tP#db2024!secure',
    'database' => 'teampass',
    'port' => 3306,
    'encoding' => 'utf8',
    'prefix' => 'teampass_',
    'cpassman_dir' => '/var/www/teampass',
    'cpassman_url' => 'https://passwords.internal.corp',
    'salt_key' => '%%FLAG%%',
    'session_duration' => 60,
    'api_token_duration' => 60,
    'duo_enabled' => false,
    'duo_ikey' => '',
    'duo_skey' => '',
    'duo_host' => '',
    'ldap_enabled' => false,
    'ldap_server' => '',
    'ldap_base_dn' => '',
    'enable_pf_feature' => true,
    'log_connections' => true,
    'pwd_maximum_length' => 100,
);
