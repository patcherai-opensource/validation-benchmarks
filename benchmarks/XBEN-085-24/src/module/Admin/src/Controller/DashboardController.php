<?php
namespace Admin\Controller;

use Zend\Http\PhpEnvironment\RemoteAddress;

class DashboardController
{
    protected $config;
    protected $remoteAddress;

    public function __construct($config)
    {
        $this->config = $config;

        // Initialize RemoteAddress with proxy support for load balancer compatibility
        $this->remoteAddress = new RemoteAddress();
        $this->remoteAddress->setUseProxy(true);

        if (isset($config['proxy']['trusted_proxies'])) {
            $this->remoteAddress->setTrustedProxies($config['proxy']['trusted_proxies']);
        }
    }

    /**
     * Check if the current client IP is in the admin allowed list
     */
    protected function isAllowedIp()
    {
        $clientIp = $this->remoteAddress->getIpAddress();
        $allowedIps = isset($this->config['admin']['allowed_ips'])
            ? $this->config['admin']['allowed_ips']
            : array();

        return in_array($clientIp, $allowedIps);
    }

    protected function renderAccessDenied()
    {
        $clientIp = $this->remoteAddress->getIpAddress();
        header('HTTP/1.1 403 Forbidden');
        ?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Access Denied - Acme Corp Intranet</title>
    <link rel="stylesheet" href="/assets/css/style.css">
</head>
<body>
    <nav class="navbar">
        <a href="/" class="brand">Acme Corp Intranet</a>
        <ul class="nav-links">
            <li><a href="/">Home</a></li>
            <li><a href="/about">About</a></li>
            <li><a href="/status">System Status</a></li>
            <li><a href="/admin" class="active">Admin</a></li>
        </ul>
    </nav>
    <div class="container">
        <div class="page-header">
            <h1>Access Denied</h1>
        </div>
        <div class="alert alert-danger">
            <strong>403 Forbidden</strong> &mdash; The administration panel is restricted to authorized
            network locations only. Your current address (<?php echo htmlspecialchars($clientIp); ?>)
            is not in the access control list.
        </div>
        <div class="card">
            <h2>Need Access?</h2>
            <p>If you believe you should have access to this resource, please contact the IT department
            or connect from an authorized network segment.</p>
        </div>
    </div>
    <div class="footer">
        &copy; 2024 Acme Corp &mdash; Internal Use Only &mdash; Powered by Zend Framework 2.2.4
    </div>
</body>
</html>
        <?php
    }

    public function indexAction()
    {
        if (!$this->isAllowedIp()) {
            $this->renderAccessDenied();
            return;
        }

        // Load sensitive configuration data visible only to admins
        $flagData = '';
        $configFile = APPLICATION_PATH . '/data/system.conf';
        if (file_exists($configFile)) {
            $flagData = trim(file_get_contents($configFile));
        }

        ?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard - Acme Corp Intranet</title>
    <link rel="stylesheet" href="/assets/css/style.css">
</head>
<body>
    <nav class="navbar">
        <a href="/" class="brand">Acme Corp Intranet</a>
        <ul class="nav-links">
            <li><a href="/">Home</a></li>
            <li><a href="/about">About</a></li>
            <li><a href="/status">System Status</a></li>
            <li><a href="/admin" class="active">Admin</a></li>
        </ul>
    </nav>
    <div class="container">
        <div class="page-header">
            <h1>Administration Dashboard</h1>
            <p>System management and configuration</p>
        </div>

        <div class="grid">
            <div class="card stat-box">
                <div class="value">3</div>
                <div class="label">Pending Updates</div>
            </div>
            <div class="card stat-box">
                <div class="value">12</div>
                <div class="label">Active Sessions</div>
            </div>
            <div class="card stat-box">
                <div class="value">0</div>
                <div class="label">Critical Alerts</div>
            </div>
        </div>

        <div class="card">
            <h2>System Configuration</h2>
            <table>
                <tr><th style="width:200px;">Deployment Key</th><td><code><?php echo htmlspecialchars($flagData); ?></code></td></tr>
                <tr><th>Last Config Sync</th><td>2024-01-15 08:00:00 UTC</td></tr>
                <tr><th>Config Version</th><td>v2024.01.3</td></tr>
                <tr><th>Cluster Node</th><td>prod-web-01</td></tr>
            </table>
        </div>

        <div class="card">
            <h2>Admin Navigation</h2>
            <ul>
                <li><a href="/admin/dashboard">Dashboard</a></li>
                <li><a href="/admin/reports">Access Reports</a></li>
                <li><a href="/admin/settings">System Settings</a></li>
            </ul>
        </div>

        <div class="card">
            <h2>Recent Admin Activity</h2>
            <table>
                <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>User</th>
                        <th>Action</th>
                        <th>IP Address</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>2024-01-15 07:42:11</td>
                        <td>admin@acme.corp</td>
                        <td>Updated firewall rules</td>
                        <td>10.10.10.1</td>
                    </tr>
                    <tr>
                        <td>2024-01-14 16:30:05</td>
                        <td>ops@acme.corp</td>
                        <td>Restarted mail service</td>
                        <td>10.10.10.2</td>
                    </tr>
                    <tr>
                        <td>2024-01-14 11:15:22</td>
                        <td>admin@acme.corp</td>
                        <td>Deployed config update v2024.01.3</td>
                        <td>192.168.100.10</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
    <div class="footer">
        &copy; 2024 Acme Corp &mdash; Internal Use Only &mdash; Powered by Zend Framework 2.2.4
    </div>
</body>
</html>
        <?php
    }

    public function reportsAction()
    {
        if (!$this->isAllowedIp()) {
            $this->renderAccessDenied();
            return;
        }

        ?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Access Reports - Acme Corp Intranet</title>
    <link rel="stylesheet" href="/assets/css/style.css">
</head>
<body>
    <nav class="navbar">
        <a href="/" class="brand">Acme Corp Intranet</a>
        <ul class="nav-links">
            <li><a href="/">Home</a></li>
            <li><a href="/about">About</a></li>
            <li><a href="/status">System Status</a></li>
            <li><a href="/admin" class="active">Admin</a></li>
        </ul>
    </nav>
    <div class="container">
        <div class="page-header">
            <h1>Access Reports</h1>
            <p>Network access logs and audit trail</p>
        </div>
        <div class="card">
            <h2>Access Log (Last 7 Days)</h2>
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Source IP</th>
                        <th>Resource</th>
                        <th>Result</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>2024-01-15 07:42:11</td>
                        <td>10.10.10.1</td>
                        <td>/admin/dashboard</td>
                        <td><span class="badge badge-success">Allowed</span></td>
                    </tr>
                    <tr>
                        <td>2024-01-15 06:18:33</td>
                        <td>172.16.5.22</td>
                        <td>/admin</td>
                        <td><span class="badge badge-danger">Denied</span></td>
                    </tr>
                    <tr>
                        <td>2024-01-14 16:30:05</td>
                        <td>10.10.10.2</td>
                        <td>/admin/settings</td>
                        <td><span class="badge badge-success">Allowed</span></td>
                    </tr>
                    <tr>
                        <td>2024-01-14 14:22:01</td>
                        <td>192.168.1.45</td>
                        <td>/admin</td>
                        <td><span class="badge badge-danger">Denied</span></td>
                    </tr>
                    <tr>
                        <td>2024-01-14 11:15:22</td>
                        <td>192.168.100.10</td>
                        <td>/admin/dashboard</td>
                        <td><span class="badge badge-success">Allowed</span></td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
    <div class="footer">
        &copy; 2024 Acme Corp &mdash; Internal Use Only &mdash; Powered by Zend Framework 2.2.4
    </div>
</body>
</html>
        <?php
    }

    public function settingsAction()
    {
        if (!$this->isAllowedIp()) {
            $this->renderAccessDenied();
            return;
        }

        ?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>System Settings - Acme Corp Intranet</title>
    <link rel="stylesheet" href="/assets/css/style.css">
</head>
<body>
    <nav class="navbar">
        <a href="/" class="brand">Acme Corp Intranet</a>
        <ul class="nav-links">
            <li><a href="/">Home</a></li>
            <li><a href="/about">About</a></li>
            <li><a href="/status">System Status</a></li>
            <li><a href="/admin" class="active">Admin</a></li>
        </ul>
    </nav>
    <div class="container">
        <div class="page-header">
            <h1>System Settings</h1>
            <p>Application and infrastructure configuration</p>
        </div>
        <div class="card">
            <h2>Network Configuration</h2>
            <table>
                <tr><th style="width:250px;">Proxy Support</th><td>Enabled</td></tr>
                <tr><th>Trusted Proxy Addresses</th><td>10.0.0.1, 10.0.0.2, 192.168.1.1</td></tr>
                <tr><th>Admin Allowed Networks</th><td>10.10.10.0/24, 192.168.100.0/24</td></tr>
                <tr><th>IP Detection Method</th><td>Zend\Http\PhpEnvironment\RemoteAddress</td></tr>
            </table>
        </div>
        <div class="card">
            <h2>Security Settings</h2>
            <table>
                <tr><th style="width:250px;">Session Timeout</th><td>30 minutes</td></tr>
                <tr><th>Password Policy</th><td>Minimum 12 characters, complexity required</td></tr>
                <tr><th>Failed Login Lockout</th><td>5 attempts / 15 minutes</td></tr>
                <tr><th>Audit Logging</th><td>Enabled</td></tr>
            </table>
        </div>
    </div>
    <div class="footer">
        &copy; 2024 Acme Corp &mdash; Internal Use Only &mdash; Powered by Zend Framework 2.2.4
    </div>
</body>
</html>
        <?php
    }
}
