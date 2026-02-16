<?php
/**
 * Request Handler
 * 
 * Handles incoming HTTP request data, IP resolution,
 * and server variable access.
 */

class Request
{
    protected $clientAddress = '';
    protected $serverVars = [];
    protected $headers = [];

    public function __construct()
    {
        $this->serverVars = $_SERVER;
        $this->headers = $this->parseHeaders();
    }

    /**
     * Resolves the client's IP address.
     * 
     * When running behind a reverse proxy, the client IP is typically
     * provided via forwarding headers. The trustedProxies configuration
     * determines which upstream proxies are trusted to provide this info.
     *
     * @return string The resolved IP address
     */
    public function resolveClientAddress(): string
    {
        if ($this->clientAddress !== '') {
            return $this->clientAddress;
        }

        $config = require __DIR__ . '/../config/app.php';
        $trustedProxies = $config['trustedProxies'] ?? '';

        if (!empty($trustedProxies) && !is_array($trustedProxies)) {
            $trustedProxies = explode(',', str_replace(' ', '', $trustedProxies));
        }

        $this->clientAddress = $this->serverVars['REMOTE_ADDR'] ?? '0.0.0.0';

        // Process forwarding headers if proxy configuration exists
        if ($trustedProxies) {
            $forwardHeaders = [
                'x-forwarded-for',
                'client-ip',
                'x-client-ip',
                'x-cluster-client-ip',
            ];

            $spoofedAddr = null;

            foreach ($forwardHeaders as $headerName) {
                if (isset($this->headers[$headerName])) {
                    $value = $this->headers[$headerName];

                    // Proxies may chain addresses: client, proxy1, proxy2
                    sscanf($value, '%[^,]', $firstAddr);

                    if ($firstAddr && filter_var(trim($firstAddr), FILTER_VALIDATE_IP)) {
                        $spoofedAddr = trim($firstAddr);
                        break;
                    }
                }
            }

            if ($spoofedAddr) {
                foreach ($trustedProxies as $proxyEntry) {
                    $proxyEntry = trim($proxyEntry);
                    
                    if (strpos($proxyEntry, '/') === false) {
                        // Direct IP match
                        if ($proxyEntry === $this->clientAddress) {
                            $this->clientAddress = $spoofedAddr;
                            break;
                        }
                        continue;
                    }

                    // CIDR subnet check
                    if ($this->isInSubnet($this->clientAddress, $proxyEntry)) {
                        $this->clientAddress = $spoofedAddr;
                        break;
                    }
                }
            }
        }

        if (!filter_var($this->clientAddress, FILTER_VALIDATE_IP)) {
            $this->clientAddress = '0.0.0.0';
        }

        return $this->clientAddress;
    }

    /**
     * Check if an IP is within a CIDR subnet
     */
    protected function isInSubnet(string $ip, string $cidr): bool
    {
        list($subnet, $bits) = explode('/', $cidr);
        
        $ip = ip2long($ip);
        $subnet = ip2long($subnet);
        
        if ($ip === false || $subnet === false) {
            return false;
        }
        
        $mask = -1 << (32 - (int)$bits);
        $subnet &= $mask;
        
        return ($ip & $mask) === $subnet;
    }

    /**
     * Parse request headers into a normalized array
     */
    protected function parseHeaders(): array
    {
        $headers = [];
        foreach ($this->serverVars as $key => $value) {
            if (strpos($key, 'HTTP_') === 0) {
                $headerName = strtolower(str_replace('_', '-', substr($key, 5)));
                $headers[$headerName] = $value;
            }
        }
        return $headers;
    }

    /**
     * Get a specific header value
     */
    public function getHeader(string $name): ?string
    {
        $name = strtolower($name);
        return $this->headers[$name] ?? null;
    }

    /**
     * Get request method
     */
    public function getMethod(): string
    {
        return strtoupper($this->serverVars['REQUEST_METHOD'] ?? 'GET');
    }

    /**
     * Get request URI path
     */
    public function getPath(): string
    {
        $uri = $this->serverVars['REQUEST_URI'] ?? '/';
        $path = parse_url($uri, PHP_URL_PATH);
        return $path ?: '/';
    }

    /**
     * Get POST data
     */
    public function getPost(string $key = null)
    {
        if ($key === null) {
            return $_POST;
        }
        return $_POST[$key] ?? null;
    }

    /**
     * Get GET data
     */
    public function getQuery(string $key = null)
    {
        if ($key === null) {
            return $_GET;
        }
        return $_GET[$key] ?? null;
    }

    /**
     * Get a server variable
     */
    public function getServer(string $key): ?string
    {
        return $this->serverVars[$key] ?? null;
    }
}
