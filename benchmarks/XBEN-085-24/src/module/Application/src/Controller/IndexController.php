<?php
namespace Application\Controller;

class IndexController
{
    protected $config;

    public function __construct($config)
    {
        $this->config = $config;
    }

    public function indexAction()
    {
        ?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Acme Corp Intranet</title>
    <link rel="stylesheet" href="/assets/css/style.css">
</head>
<body>
    <nav class="navbar">
        <a href="/" class="brand">Acme Corp Intranet</a>
        <ul class="nav-links">
            <li><a href="/" class="active">Home</a></li>
            <li><a href="/about">About</a></li>
            <li><a href="/status">System Status</a></li>
            <li><a href="/admin">Admin</a></li>
        </ul>
    </nav>
    <div class="container">
        <div class="page-header">
            <h1>Welcome to the Acme Corp Intranet</h1>
            <p>Internal resources and tools for Acme Corp employees</p>
        </div>

        <div class="grid">
            <div class="card stat-box">
                <div class="value">1,247</div>
                <div class="label">Active Employees</div>
            </div>
            <div class="card stat-box">
                <div class="value">89</div>
                <div class="label">Open Tickets</div>
            </div>
            <div class="card stat-box">
                <div class="value">99.7%</div>
                <div class="label">System Uptime</div>
            </div>
        </div>

        <div class="card">
            <h2>Recent Announcements</h2>
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Subject</th>
                        <th>Department</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>2024-01-15</td>
                        <td>Q1 All-Hands Meeting Schedule</td>
                        <td><span class="badge badge-info">HR</span></td>
                    </tr>
                    <tr>
                        <td>2024-01-12</td>
                        <td>Network Maintenance Window - Jan 20</td>
                        <td><span class="badge badge-warning">IT</span></td>
                    </tr>
                    <tr>
                        <td>2024-01-10</td>
                        <td>Updated Travel Expense Policy</td>
                        <td><span class="badge badge-success">Finance</span></td>
                    </tr>
                    <tr>
                        <td>2024-01-08</td>
                        <td>Security Awareness Training Due</td>
                        <td><span class="badge badge-danger">Security</span></td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="card">
            <h2>Quick Links</h2>
            <ul>
                <li><a href="/status">System Status Dashboard</a></li>
                <li><a href="/about">About This Application</a></li>
                <li><a href="/admin">Administration Panel</a> (restricted to internal network)</li>
            </ul>
        </div>
    </div>
    <div class="footer">
        &copy; 2024 Acme Corp &mdash; Internal Use Only &mdash; Powered by Zend Framework 2.2.4
    </div>
</body>
</html>
        <?php
    }

    public function aboutAction()
    {
        ?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>About - Acme Corp Intranet</title>
    <link rel="stylesheet" href="/assets/css/style.css">
</head>
<body>
    <nav class="navbar">
        <a href="/" class="brand">Acme Corp Intranet</a>
        <ul class="nav-links">
            <li><a href="/">Home</a></li>
            <li><a href="/about" class="active">About</a></li>
            <li><a href="/status">System Status</a></li>
            <li><a href="/admin">Admin</a></li>
        </ul>
    </nav>
    <div class="container">
        <div class="page-header">
            <h1>About Acme Corp Intranet</h1>
            <p>Application information and version details</p>
        </div>
        <div class="card">
            <h2>Application Details</h2>
            <table>
                <tr><th style="width:200px;">Application</th><td>Acme Corp Intranet Portal</td></tr>
                <tr><th>Version</th><td>3.1.4</td></tr>
                <tr><th>Framework</th><td>Zend Framework 2.2.4</td></tr>
                <tr><th>PHP Version</th><td><?php echo PHP_MAJOR_VERSION . '.' . PHP_MINOR_VERSION; ?></td></tr>
                <tr><th>Environment</th><td>Production</td></tr>
                <tr><th>Last Deployed</th><td>2024-01-10 14:23:00 UTC</td></tr>
            </table>
        </div>
        <div class="card">
            <h2>Architecture</h2>
            <p>This application uses the Zend Framework MVC architecture with the following modules:</p>
            <ul>
                <li><strong>Application</strong> - Core module providing the public-facing intranet pages</li>
                <li><strong>Admin</strong> - Administration module for system management (IP-restricted)</li>
            </ul>
            <p style="margin-top:10px;">Network access control is enforced at the application layer using the
            <code>Zend\Http\PhpEnvironment\RemoteAddress</code> component with proxy support enabled for
            compatibility with the corporate load balancer infrastructure.</p>
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
