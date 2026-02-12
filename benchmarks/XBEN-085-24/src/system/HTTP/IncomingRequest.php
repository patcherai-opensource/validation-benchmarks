<?php
/**
 * CodeIgniter Incoming Request Handler
 *
 * Represents an incoming HTTP request to the application.
 *
 * @package    CodeIgniter
 * @subpackage HTTP
 */

require_once __DIR__ . '/RequestTrait.php';

class IncomingRequest
{
    use RequestTrait;

    /**
     * The URI path
     *
     * @var string
     */
    protected $uri;

    /**
     * Constructor
     *
     * @param array $config Application configuration
     */
    public function __construct(array $config = [])
    {
        $this->uri = $_SERVER['REQUEST_URI'] ?? '/';

        // Load proxy configuration
        if (isset($config['proxyIPs'])) {
            $this->proxyIPs = $config['proxyIPs'];
        }
    }

    /**
     * Get the current URI path
     *
     * @return string
     */
    public function getPath(): string
    {
        $path = parse_url($this->uri, PHP_URL_PATH);
        return $path ?: '/';
    }

    /**
     * Get user agent string
     *
     * @return string
     */
    public function getUserAgent(): string
    {
        return $_SERVER['HTTP_USER_AGENT'] ?? '';
    }

    /**
     * Check if request is AJAX
     *
     * @return bool
     */
    public function isAJAX(): bool
    {
        return isset($_SERVER['HTTP_X_REQUESTED_WITH'])
            && strtolower($_SERVER['HTTP_X_REQUESTED_WITH']) === 'xmlhttprequest';
    }
}
