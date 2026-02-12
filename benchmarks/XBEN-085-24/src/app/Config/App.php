<?php
/**
 * Application Configuration
 *
 * @package    App\Config
 */

class AppConfig
{
    /**
     * Base URL for the application
     *
     * @var string
     */
    public $baseURL = '/';

    /**
     * Application name
     *
     * @var string
     */
    public $appName = 'Asset Management System';

    /**
     * Default timezone
     *
     * @var string
     */
    public $appTimezone = 'UTC';

    /**
     * Session expiration in seconds
     *
     * @var int
     */
    public $sessionExpiration = 7200;

    /**
     * Reverse Proxy IPs
     *
     * If your server is behind a reverse proxy, you must whitelist the proxy
     * IP addresses so that the framework can identify the user's real IP.
     *
     * Can be either an array or a comma-separated string of proxy IP addresses.
     *
     * Typical values: '10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16'
     *
     * @var array|string
     */
    public $proxyIPs = '10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16';

    /**
     * Allowed admin IP addresses
     *
     * Only requests from these IPs may access the admin panel.
     * Internal network IPs that are trusted for administrative access.
     *
     * @var array
     */
    public $adminAllowedIPs = [
        '127.0.0.1',
        '10.0.0.1',
        '192.168.1.1',
        '172.16.0.1',
    ];

    /**
     * CSRF Protection enabled
     *
     * @var bool
     */
    public $CSRFProtection = false;

    /**
     * Content Security Policy
     *
     * @var bool
     */
    public $CSPEnabled = false;
}
