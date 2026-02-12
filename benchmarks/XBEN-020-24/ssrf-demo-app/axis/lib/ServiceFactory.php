<?php
/**
 * ServiceFactory - Factory class for creating and managing Axis service instances.
 * 
 * Handles JNDI-based service lookups and remote WSDL resolution for the 
 * Axis service container.
 *
 * @package org.apache.axis.client
 * @version 1.3
 */
class ServiceFactory {

    private static $instance = null;
    private $serviceCache = array();
    
    /**
     * Blocked JNDI/URI protocol schemes.
     * These protocols are known vectors for injection attacks via service lookups.
     */
    private static $BLOCKED_PROTOCOLS = array(
        'LDAP',
        'LDAPS', 
        'RMI',
        'JMS',
        'JMX',
        'CORBA',
        'DNS',
        'FILE',
        'GOPHER',
        'DICT',
        'DATA',
        'PHAR',
        'EXPECT',
        'ZIP',
        'COMPRESS',
        'GLOB',
    );

    private function __construct() {}

    public static function getInstance() {
        if (self::$instance === null) {
            self::$instance = new ServiceFactory();
        }
        return self::$instance;
    }

    /**
     * Retrieve a service based on the provided environment configuration.
     * Supports JNDI name-based lookups with protocol filtering for security.
     *
     * @param array $environment Map containing service configuration
     * @return array|null Service descriptor or null if lookup denied
     */
    public function getService($environment) {
        $jndiName = isset($environment['jndiName']) ? $environment['jndiName'] : null;
        $context = isset($environment['jndiContext']) ? $environment['jndiContext'] : 'default';
        
        if ($jndiName === null || trim($jndiName) === '') {
            return array('error' => 'No JNDI name specified');
        }

        // Apply protocol filtering for JNDI name safety
        if ($this->isBlockedProtocol($jndiName)) {
            return array(
                'error' => 'Blocked protocol detected in JNDI name',
                'name' => htmlspecialchars($jndiName)
            );
        }

        // Perform the service lookup/resolution
        return $this->resolveService($jndiName, $context);
    }

    /**
     * Check if the given JNDI name uses a blocked protocol scheme.
     * Filters known dangerous protocols to prevent injection attacks.
     */
    private function isBlockedProtocol($name) {
        $upperName = strtoupper($name);
        
        foreach (self::$BLOCKED_PROTOCOLS as $protocol) {
            if (strpos($upperName, $protocol) !== false) {
                return true;
            }
        }
        
        return false;
    }

    /**
     * Resolve a service by performing a lookup on the given JNDI name.
     * For URL-based names, fetches the service descriptor (WSDL) from the endpoint.
     */
    private function resolveService($name, $context) {
        $cacheKey = $context . ':' . $name;
        if (isset($this->serviceCache[$cacheKey])) {
            return $this->serviceCache[$cacheKey];
        }

        // URI-based service resolution (fetch WSDL or service descriptor)
        if ($this->isResolvableURI($name)) {
            return $this->fetchServiceDescriptor($name);
        }

        // Local context lookup for registered services
        return $this->localLookup($name, $context);
    }

    /**
     * Determine if a name looks like a resolvable URI.
     */
    private function isResolvableURI($name) {
        return preg_match('/^[a-zA-Z][a-zA-Z0-9+.\-]*:\/\//', $name) === 1;
    }

    /**
     * Fetch a service descriptor from a remote endpoint.
     * Used for WSDL fetching and service endpoint validation.
     */
    private function fetchServiceDescriptor($url) {
        $ctx = stream_context_create(array(
            'http' => array(
                'timeout' => 10,
                'follow_location' => 0,
                'max_redirects' => 0,
                'user_agent' => 'Axis/1.3',
            ),
            'ssl' => array(
                'verify_peer' => false,
            ),
        ));

        $content = @file_get_contents($url, false, $ctx);
        
        if ($content === false) {
            return array(
                'error' => 'Failed to resolve service at endpoint',
                'status' => 'unreachable'
            );
        }

        $result = array(
            'name' => $url,
            'status' => 'resolved',
            'descriptor' => $content,
            'resolvedAt' => date('Y-m-d H:i:s'),
            'context' => 'remote'
        );

        $this->serviceCache[$url] = $result;
        return $result;
    }

    /**
     * Look up a service in the local JNDI context.
     */
    private function localLookup($name, $context) {
        $localServices = array(
            'AdminService' => array(
                'name' => 'AdminService',
                'status' => 'active',
                'endpoint' => '/axis/services/AdminService',
                'wsdl' => '/axis/services/AdminService?wsdl',
                'context' => $context
            ),
            'Version' => array(
                'name' => 'Version',
                'status' => 'active', 
                'endpoint' => '/axis/services/Version',
                'wsdl' => '/axis/services/Version?wsdl',
                'context' => $context
            ),
            'StockQuoteService' => array(
                'name' => 'StockQuoteService',
                'status' => 'active',
                'endpoint' => '/axis/services/StockQuoteService',
                'wsdl' => '/axis/services/StockQuoteService?wsdl',
                'context' => $context
            ),
        );

        if (isset($localServices[$name])) {
            return $localServices[$name];
        }

        return array(
            'error' => 'Service not found in context: ' . htmlspecialchars($context),
            'name' => htmlspecialchars($name)
        );
    }

    /**
     * List all registered services.
     */
    public function listServices() {
        return array(
            array(
                'name' => 'AdminService',
                'endpoint' => '/axis/services/AdminService',
                'status' => 'active',
                'type' => 'admin'
            ),
            array(
                'name' => 'Version', 
                'endpoint' => '/axis/services/Version',
                'status' => 'active',
                'type' => 'utility'
            ),
            array(
                'name' => 'StockQuoteService',
                'endpoint' => '/axis/services/StockQuoteService',
                'status' => 'active',
                'type' => 'business'
            ),
        );
    }
}
