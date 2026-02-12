<?php
/**
 * Admin Controller
 *
 * Handles administrative functions. Access is restricted to
 * whitelisted IP addresses defined in the application configuration.
 *
 * @package    App\Controllers
 */

require_once __DIR__ . '/../Middleware/IPFilter.php';

class AdminController
{
    protected $request;
    protected $config;

    public function __construct($request, $config)
    {
        $this->request = $request;
        $this->config = $config;
    }

    /**
     * Admin panel index - shows system configuration and internal data
     */
    public function index(): string
    {
        $clientIP = $this->request->getIPAddress();
        $allowed = IPFilter::isAllowed($this->request, $this->config->adminAllowedIPs);
        IPFilter::logAccess($clientIP, '/admin', $allowed);

        if (! $allowed) {
            http_response_code(403);
            return $this->renderForbidden($clientIP);
        }

        return $this->renderView('admin/index', [
            'clientIP' => $clientIP,
        ]);
    }

    /**
     * System configuration page
     */
    public function config(): string
    {
        $clientIP = $this->request->getIPAddress();
        $allowed = IPFilter::isAllowed($this->request, $this->config->adminAllowedIPs);
        IPFilter::logAccess($clientIP, '/admin/config', $allowed);

        if (! $allowed) {
            http_response_code(403);
            return $this->renderForbidden($clientIP);
        }

        return $this->renderView('admin/config', [
            'clientIP' => $clientIP,
        ]);
    }

    /**
     * Export system report - contains sensitive operational data
     */
    public function report(): string
    {
        $clientIP = $this->request->getIPAddress();
        $allowed = IPFilter::isAllowed($this->request, $this->config->adminAllowedIPs);
        IPFilter::logAccess($clientIP, '/admin/report', $allowed);

        if (! $allowed) {
            http_response_code(403);
            return $this->renderForbidden($clientIP);
        }

        $reportData = $this->generateSystemReport();
        return $this->renderView('admin/report', [
            'clientIP' => $clientIP,
            'report'   => $reportData,
        ]);
    }

    /**
     * Generate system report with operational data
     */
    private function generateSystemReport(): array
    {
        $flagFile = '/var/www/data/system_key.conf';
        $systemKey = 'UNAVAILABLE';
        if (file_exists($flagFile)) {
            $systemKey = trim(file_get_contents($flagFile));
        }

        return [
            'generated_at'   => date('Y-m-d H:i:s'),
            'server_name'    => gethostname(),
            'php_version'    => phpversion(),
            'uptime'         => $this->getUptime(),
            'memory_usage'   => round(memory_get_usage(true) / 1024 / 1024, 2) . ' MB',
            'disk_usage'     => $this->getDiskUsage(),
            'active_sessions' => $this->getActiveSessions(),
            'system_key'     => $systemKey,
            'last_backup'    => date('Y-m-d', strtotime('-2 days')),
            'db_status'      => 'connected',
        ];
    }

    /**
     * Get system uptime
     */
    private function getUptime(): string
    {
        if (file_exists('/proc/uptime')) {
            $uptime = file_get_contents('/proc/uptime');
            $seconds = (int) explode(' ', $uptime)[0];
            $days = floor($seconds / 86400);
            $hours = floor(($seconds % 86400) / 3600);
            return "{$days}d {$hours}h";
        }
        return 'N/A';
    }

    /**
     * Get disk usage statistics
     */
    private function getDiskUsage(): string
    {
        $free = disk_free_space('/');
        $total = disk_total_space('/');
        if ($total > 0) {
            $used = round((1 - $free / $total) * 100, 1);
            return "{$used}%";
        }
        return 'N/A';
    }

    /**
     * Get count of active sessions
     */
    private function getActiveSessions(): int
    {
        $sessionPath = session_save_path();
        if (empty($sessionPath)) {
            $sessionPath = '/tmp';
        }
        $files = glob($sessionPath . '/sess_*');
        return $files ? count($files) : 0;
    }

    /**
     * Render forbidden access page
     */
    private function renderForbidden(string $ip): string
    {
        ob_start();
        include __DIR__ . '/../Views/errors/forbidden.php';
        return ob_get_clean();
    }

    /**
     * Render a view template
     */
    private function renderView(string $view, array $data = []): string
    {
        extract($data);
        ob_start();
        $viewPath = __DIR__ . '/../Views/' . $view . '.php';
        if (file_exists($viewPath)) {
            include $viewPath;
        }
        return ob_get_clean();
    }
}
