<?php
/**
 * Global Configuration Override
 *
 * You can use this file for overriding configuration values from modules, etc.
 * You would place values in here that are agnostic to the environment and not
 * having sensitive information.
 */
return array(
    'db' => array(
        'driver' => 'Pdo',
        'dsn'    => 'sqlite:' . __DIR__ . '/../../data/app.db',
    ),
    'proxy' => array(
        'use_proxy' => true,
        'trusted_proxies' => array(
            '10.0.0.1',
            '10.0.0.2',
            '192.168.1.1',
        ),
    ),
    'admin' => array(
        'allowed_ips' => array(
            '10.10.10.1',
            '10.10.10.2',
            '192.168.100.10',
        ),
    ),
);
