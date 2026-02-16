<?php
/**
 * Admin Controller
 * 
 * Administrative panel - restricted to internal network access only.
 * Access is validated against the resolved client IP address.
 */

class AdminController
{
    protected $request;
    protected $response;

    public function __construct(Request $request, Response $response)
    {
        $this->request = $request;
        $this->response = $response;
    }

    /**
     * Verify the requesting client is on an allowed network
     */
    protected function verifyNetworkAccess(): bool
    {
        $config = require __DIR__ . '/../config/app.php';
        $allowedNetworks = $config['adminAllowedNetworks'] ?? [];
        $clientIP = $this->request->resolveClientAddress();

        foreach ($allowedNetworks as $network) {
            if ($this->isAddressInRange($clientIP, $network)) {
                return true;
            }
        }

        return false;
    }

    /**
     * Check if IP falls within a CIDR range
     */
    protected function isAddressInRange(string $ip, string $cidr): bool
    {
        if (strpos($cidr, '/') === false) {
            return $ip === $cidr;
        }

        list($subnet, $bits) = explode('/', $cidr);

        $ipLong = ip2long($ip);
        $subnetLong = ip2long($subnet);

        if ($ipLong === false || $subnetLong === false) {
            return false;
        }

        $mask = -1 << (32 - (int)$bits);
        return ($ipLong & $mask) === ($subnetLong & $mask);
    }

    /**
     * Admin panel overview
     */
    public function panel(): void
    {
        if (!$this->verifyNetworkAccess()) {
            $clientIP = $this->request->resolveClientAddress();
            http_response_code(403);
            $data = [
                'clientIP' => $clientIP,
            ];
            include __DIR__ . '/../views/restricted.php';
            return;
        }

        $config = require __DIR__ . '/../config/app.php';

        // Load system secrets for the admin view
        $secretToken = 'N/A';
        $secretFile = '/var/www/config/secret.php';
        if (file_exists($secretFile)) {
            include $secretFile;
            if (defined('SYSTEM_SECRET_TOKEN')) {
                $secretToken = SYSTEM_SECRET_TOKEN;
            }
        }

        $data = [
            'appName' => $config['appName'],
            'clientIP' => $this->request->resolveClientAddress(),
            'serverTime' => gmdate('Y-m-d H:i:s T'),
            'phpVersion' => phpversion(),
            'systemLoad' => sys_getloadavg(),
            'memoryUsage' => round(memory_get_usage(true) / 1024 / 1024, 2),
            'diskFree' => round(disk_free_space('/') / 1024 / 1024 / 1024, 2),
            'secretToken' => $secretToken,
            'uptime' => @file_get_contents('/proc/uptime') ?: 'N/A',
        ];

        include __DIR__ . '/../views/panel.php';
    }

    /**
     * Network diagnostics endpoint
     */
    public function diagnostics(): void
    {
        if (!$this->verifyNetworkAccess()) {
            http_response_code(403);
            $this->response->json([
                'error' => 'Access denied',
                'message' => 'This endpoint is restricted to internal networks.',
            ], 403);
            return;
        }

        $this->response->json([
            'hostname' => gethostname(),
            'server_addr' => $_SERVER['SERVER_ADDR'] ?? 'unknown',
            'server_port' => $_SERVER['SERVER_PORT'] ?? 'unknown',
            'document_root' => $_SERVER['DOCUMENT_ROOT'] ?? 'unknown',
            'remote_addr' => $_SERVER['REMOTE_ADDR'] ?? 'unknown',
            'resolved_client_ip' => $this->request->resolveClientAddress(),
        ]);
    }
}
