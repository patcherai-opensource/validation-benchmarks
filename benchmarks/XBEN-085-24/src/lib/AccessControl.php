<?php
/**
 * Access Control Layer
 *
 * Handles IP-based access restrictions for sensitive areas of the application.
 * Uses ClientAddress to resolve the real client IP, supporting deployments
 * behind load balancers and reverse proxies.
 *
 * @package  AppCore\Security
 * @license  BSD-3-Clause
 */

namespace AppCore\Security;

require_once __DIR__ . '/ClientAddress.php';

use AppCore\Network\ClientAddress;

class AccessControl
{
    /**
     * @var ClientAddress
     */
    protected $addressResolver;

    /**
     * List of IP ranges/addresses allowed to access restricted areas
     *
     * @var array
     */
    protected $allowedNetworks = array();

    /**
     * Constructor
     *
     * @param array $config Configuration array
     */
    public function __construct(array $config = array())
    {
        $this->addressResolver = new ClientAddress();

        // Enable proxy support if configured (typical for production deployments)
        if (isset($config['proxy_enabled']) && $config['proxy_enabled']) {
            $this->addressResolver->setProxyEnabled(true);
        }

        if (isset($config['known_proxies'])) {
            $this->addressResolver->setKnownProxies($config['known_proxies']);
        }

        if (isset($config['forward_header'])) {
            $this->addressResolver->setForwardHeader($config['forward_header']);
        }

        if (isset($config['allowed_networks'])) {
            $this->allowedNetworks = $config['allowed_networks'];
        }
    }

    /**
     * Check if the current request originates from an allowed network
     *
     * @return bool
     */
    public function isAllowed()
    {
        $clientIp = $this->addressResolver->resolveAddress();
        return in_array($clientIp, $this->allowedNetworks);
    }

    /**
     * Get the resolved client IP address
     *
     * @return string
     */
    public function getClientIp()
    {
        return $this->addressResolver->resolveAddress();
    }
}
