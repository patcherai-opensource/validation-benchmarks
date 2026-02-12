<?php
/**
 * Zend Framework (http://framework.zend.com/)
 *
 * @link      http://github.com/zendframework/zf2 for the canonical source repository
 * @copyright Copyright (c) 2005-2013 Zend Technologies USA Inc. (http://www.zend.com)
 * @license   http://framework.zend.com/license/new-bsd New BSD License
 */

namespace Zend\Http\PhpEnvironment;

/**
 * Detect the client's IP address based on the environment variables
 * available. Optionally, the proxy configuration can be enabled to
 * allow detection of the client's IP address behind a proxy.
 */
class RemoteAddress
{
    /**
     * Whether to use proxy addresses or not.
     *
     * As default this setting is disabled - IP address is mostly needed to increase
     * security. HTTP_* are not reliable since can easily be spoofed. It can be enabled
     * just for more flexibility, but if user uses proxy to connect to trusted services
     * it's his/her own risk, only reliable field for IP address is $_SERVER['REMOTE_ADDR'].
     *
     * @var bool
     */
    protected $useProxy = false;

    /**
     * List of trusted proxy IP addresses
     *
     * @var array
     */
    protected $trustedProxies = array();

    /**
     * HTTP header to introspect for proxies
     *
     * @var string
     */
    protected $proxyHeader = 'HTTP_X_FORWARDED_FOR';

    /**
     * Changes proxy handling setting.
     *
     * This must be static method, since validators are not aware of
     * the adapter provides its own proxy support.
     *
     * @param  bool $useProxy
     * @return RemoteAddress
     */
    public function setUseProxy($useProxy = true)
    {
        $this->useProxy = $useProxy;
        return $this;
    }

    /**
     * Checks proxy handling setting.
     *
     * @return bool Current setting value.
     */
    public function getUseProxy()
    {
        return $this->useProxy;
    }

    /**
     * Set list of trusted proxy addresses
     *
     * @param  array $trustedProxies
     * @return RemoteAddress
     */
    public function setTrustedProxies(array $trustedProxies)
    {
        $this->trustedProxies = $trustedProxies;
        return $this;
    }

    /**
     * Set the header to introspect for proxy IPs
     *
     * @param  string $header
     * @return RemoteAddress
     */
    public function setProxyHeader($header = 'X-Forwarded-For')
    {
        $this->proxyHeader = 'HTTP_' . strtoupper(str_replace('-', '_', $header));
        return $this;
    }

    /**
     * Returns client IP address.
     *
     * @return string IP address.
     */
    public function getIpAddress()
    {
        $ip = $this->getIpAddressFromProxy();
        if ($ip) {
            return $ip;
        }

        // Direct IP address
        if (isset($_SERVER['REMOTE_ADDR'])) {
            return $_SERVER['REMOTE_ADDR'];
        }

        return '';
    }

    /**
     * Attempt to get the IP address for a proxied client
     *
     * @see http://tools.ietf.org/html/draft-ietf-appsawg-http-forwarded-10#section-5.2
     * @return false|string
     */
    protected function getIpAddressFromProxy()
    {
        if (!$this->useProxy
            || !isset($_SERVER[$this->proxyHeader])
        ) {
            return false;
        }

        $header = $_SERVER[$this->proxyHeader];
        if (is_string($header)) {
            // Extract IPs
            $ips = explode(',', $header);
            // trim, so we can compare against trusted proxies properly
            $ips = array_map('trim', $ips);

            // remove trusted proxy IPs from the list
            $ips = array_diff($ips, $this->trustedProxies);

            // Any address left is the client's IP
            if (!empty($ips)) {
                return array_pop($ips);
            }
        }

        return false;
    }
}
