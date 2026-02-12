<?php
/**
 * Application configuration
 */
return array(
    'modules' => array(
        'Application',
        'Admin',
    ),
    'module_listener_options' => array(
        'module_paths' => array(
            './module',
        ),
        'config_glob_paths' => array(
            'config/autoload/{,*.}{global,local}.php',
        ),
    ),
    'service_manager' => array(
        'factories' => array(),
    ),
);
