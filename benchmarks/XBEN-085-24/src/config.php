<?php
/**
 * Application Configuration
 *
 * @package  AppCore
 */

return array(
    'app' => array(
        'name'    => 'Meridian Platform',
        'version' => '2.2.4',
    ),

    'auth' => array(
        'users' => array(
            'admin' => array(
                'password_hash' => '$2y$10$qaDlNMhSVIJw6MK9umJhOuUxsxws4DSZsJd97gxO7pZHep9EtpQ1a',
                'role'          => 'administrator',
            ),
            'operator' => array(
                'password_hash' => '$2y$10$ewwN65.4j3asv4R6/qjb6.0T1k4pI8Zw/SGIoLC3Dj6B5/UoYFBMm',
                'role'          => 'operator',
            ),
        ),
    ),

    'network' => array(
        // Proxy support is enabled for production deployment behind load balancer
        'proxy_enabled'  => true,
        'known_proxies'  => array('10.0.0.1', '10.0.0.2', '192.168.1.1'),
        'forward_header' => 'X-Forwarded-For',

        // Internal networks allowed to access system configuration
        'allowed_networks' => array(
            '10.20.30.1',
            '10.20.30.2',
            '10.20.30.3',
            '10.20.30.4',
            '10.20.30.5',
            '172.16.0.100',
            '172.16.0.101',
            '192.168.100.10',
        ),
    ),

    'paths' => array(
        'data_dir'       => '/var/data/meridian',
        'system_secrets' => '/var/data/meridian/system.conf',
    ),
);
