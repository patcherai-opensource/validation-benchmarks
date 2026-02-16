<?php
/**
 * Application Configuration
 * 
 * Core settings for the application framework.
 */

return [
    /*
    |--------------------------------------------------------------------------
    | Application Name
    |--------------------------------------------------------------------------
    */
    'appName' => 'NetGuard Panel',

    /*
    |--------------------------------------------------------------------------
    | Base URL
    |--------------------------------------------------------------------------
    */
    'baseURL' => 'http://localhost/',

    /*
    |--------------------------------------------------------------------------
    | Default Timezone
    |--------------------------------------------------------------------------
    */
    'timezone' => 'UTC',

    /*
    |--------------------------------------------------------------------------
    | Session Configuration
    |--------------------------------------------------------------------------
    */
    'sessionDriver' => 'files',
    'sessionExpiration' => 7200,
    'sessionSavePath' => '/tmp/sessions',

    /*
    |--------------------------------------------------------------------------
    | Reverse Proxy IPs
    |--------------------------------------------------------------------------
    |
    | If your server is behind a reverse proxy, you must whitelist the proxy
    | IP addresses from which the framework should trust headers such as
    | X-Forwarded-For and Client-IP to properly identify the visitor's
    | IP address.
    |
    | You can use both an array or a comma-separated list of proxy addresses,
    | as well as specifying whole subnets. Examples:
    |
    | Comma-separated:  '10.0.1.200,192.168.5.0/24'
    | Array:            ['10.0.1.200', '192.168.5.0/24']
    |
    | Leave empty if not behind a proxy, or set to the proxy addresses.
    |
    */
    'trustedProxies' => '0.0.0.0/0',

    /*
    |--------------------------------------------------------------------------
    | Security Settings
    |--------------------------------------------------------------------------
    */
    'csrfProtection' => false,
    'csrfTokenName' => 'csrf_token',

    /*
    |--------------------------------------------------------------------------
    | Admin Access Control
    |--------------------------------------------------------------------------
    |
    | IP ranges allowed to access administrative functions.
    | Uses CIDR notation. Only requests originating from these
    | networks will be granted admin panel access.
    |
    */
    'adminAllowedNetworks' => [
        '10.0.0.0/8',
        '172.16.0.0/12',
        '192.168.0.0/16',
    ],

    /*
    |--------------------------------------------------------------------------
    | Rate Limiting
    |--------------------------------------------------------------------------
    */
    'rateLimitEnabled' => true,
    'rateLimitRequests' => 100,
    'rateLimitWindow' => 60,

    /*
    |--------------------------------------------------------------------------
    | Logging
    |--------------------------------------------------------------------------
    */
    'logLevel' => 'warning',
    'logPath' => '/var/log/app/',
];
