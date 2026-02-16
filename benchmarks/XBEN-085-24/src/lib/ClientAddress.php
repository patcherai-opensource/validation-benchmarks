<?php
/**
 * Network Environment Utilities
 *
 * Provides functionality for determining client IP address,
 * with support for proxy-forwarded addresses.
 *
 * @package  AppCore\Network
 * @license  BSD-3-Clause
 */

namespace AppCore\Network;

class ClientAddress
{
    /**
     * Whether to use proxy addresses or not.
     *
     * When enabled, the class will look at proxy headers for the real client IP.
     * This is needed for applications behind load balancers or reverse proxies.
     *
     * @var bool
     */
    protected $proxyEnabled = false;

    /**
     * List of trusted proxy IP addresses
     *
     * @var array
     */
    protected $knownProxies = array();

    /**
     * HTTP header to introspect for proxied client addresses
     *
     * @var string
     */
    protected $forwardHeader = 'HTTP_X_FORWARDED_FOR';

    /**
     * Enable or disable proxy support.
     *
     * @param  bool $enable Whether to check proxied IP addresses.
     * @return ClientAddress
     */
    public function setProxyEnabled($enable = true)
    {
        $this->proxyEnabled = $enable;
        return $this;
    }

    /**
     * Check if proxy support is enabled.
     *
     * @return bool
     */
    public function getProxyEnabled()
    {
        return $this->proxyEnabled;
    }

    /**
     * Set list of trusted proxy addresses
     *
     * @param  array $proxies
     * @return ClientAddress
     */
    public function setKnownProxies(array $proxies)
    {
        $this->knownProxies = $proxies;
        return $this;
    }

    /**
     * Set the header to introspect for proxied IPs
     *
     * @param  string $header
     * @return ClientAddress
     */
    public function setForwardHeader($header = 'X-Forwarded-For')
    {
        $this->forwardHeader = $this->normalizeHeaderName($header);
        return $this;
    }

    /**
     * Returns client IP address.
     *
     * @return string IP address.
     */
    public function resolveAddress()
    {
        $ip = $this->resolveFromProxy();
        if ($ip) {
            return $ip;
        }

        if (isset($_SERVER['REMOTE_ADDR'])) {
            return $_SERVER['REMOTE_ADDR'];
        }

        return '';
    }

    /**
     * Attempt to get the IP address for a proxied client
     *
     * @return false|string
     */
    protected function resolveFromProxy()
    {
        if (!$this->proxyEnabled) {
            return false;
        }

        $header = $this->forwardHeader;

        if (!isset($_SERVER[$header]) || empty($_SERVER[$header])) {
            return false;
        }

        // Extract IPs from the forwarded header
        $ips = explode(',', $_SERVER[$header]);
        $ips = array_map('trim', $ips);
        // remove known proxy IPs from the chain
        $ips = array_diff($ips, $this->knownProxies);

        if (empty($ips)) {
            return false;
        }

        // Return the right-most non-proxy IP
        $ip = array_pop($ips);
        return $ip;
    }

    /**
     * Normalize a header string to $_SERVER format
     *
     * @param  string $header
     * @return string
     */
    protected function normalizeHeaderName($header)
    {
        $header = strtoupper($header);
        $header = str_replace('-', '_', $header);
        if (0 !== strpos($header, 'HTTP_')) {
            $header = 'HTTP_' . $header;
        }
        return $header;
    }
}
