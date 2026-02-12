<?php
/**
 * CodeIgniter HTTP Request Trait
 *
 * Provides common request handling functionality including
 * IP address resolution, header parsing, and input validation.
 *
 * @package    CodeIgniter
 * @subpackage HTTP
 */

trait RequestTrait
{
    /**
     * Stores the valid IP address
     *
     * @var string|null
     */
    protected $ipAddress = null;

    /**
     * Proxy IPs configuration
     *
     * If your server is behind a reverse proxy, you must whitelist
     * the proxy IP addresses from which the framework should trust
     * headers such as X-Forwarded-For, X-Client-IP, Client-IP.
     *
     * @var array|string
     */
    protected $proxyIPs = '';

    /**
     * Gets the IP address of the current user.
     *
     * Takes proxy headers into account when $proxyIPs is configured.
     *
     * @return string IP address
     */
    public function getIPAddress(): string
    {
        if ($this->ipAddress !== null) {
            return $this->ipAddress;
        }

        // Default to REMOTE_ADDR
        $ipAddress = $_SERVER['REMOTE_ADDR'] ?? '0.0.0.0';

        // Check proxy configuration
        $proxyIPs = $this->getProxyIPs();

        if (! empty($proxyIPs)) {
            // When proxy IPs are configured, check forwarded headers
            // for the real client IP
            foreach (['HTTP_X_FORWARDED_FOR', 'HTTP_CLIENT_IP', 'HTTP_X_CLIENT_IP'] as $header) {
                if (isset($_SERVER[$header])) {
                    // X-Forwarded-For can contain multiple IPs separated by commas
                    $ips = explode(',', $_SERVER[$header]);
                    $ipAddress = trim($ips[0]);
                    break;
                }
            }
        }

        if (! $this->isValidIP($ipAddress)) {
            $ipAddress = '0.0.0.0';
        }

        $this->ipAddress = $ipAddress;
        return $this->ipAddress;
    }

    /**
     * Retrieves the proxy IPs configuration
     *
     * @return array|string
     */
    protected function getProxyIPs()
    {
        return $this->proxyIPs;
    }

    /**
     * Validates an IP address
     *
     * @param string $ip
     * @return bool
     */
    public function isValidIP(string $ip): bool
    {
        return filter_var($ip, FILTER_VALIDATE_IP) !== false;
    }

    /**
     * Get a request header value
     *
     * @param string $name
     * @return string|null
     */
    public function getHeader(string $name): ?string
    {
        $key = 'HTTP_' . strtoupper(str_replace('-', '_', $name));
        return $_SERVER[$key] ?? null;
    }

    /**
     * Get the request method
     *
     * @return string
     */
    public function getMethod(): string
    {
        return $_SERVER['REQUEST_METHOD'] ?? 'GET';
    }

    /**
     * Get a GET parameter
     *
     * @param string $key
     * @param mixed $default
     * @return mixed
     */
    public function getGet(string $key, $default = null)
    {
        return $_GET[$key] ?? $default;
    }

    /**
     * Get a POST parameter
     *
     * @param string $key
     * @param mixed $default
     * @return mixed
     */
    public function getPost(string $key, $default = null)
    {
        return $_POST[$key] ?? $default;
    }
}
