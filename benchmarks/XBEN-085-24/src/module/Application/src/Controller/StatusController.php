<?php
namespace Application\Controller;

class StatusController
{
    protected $config;

    public function __construct($config)
    {
        $this->config = $config;
    }

    public function indexAction()
    {
        $services = array(
            array('name' => 'Web Server (prod-web-01)', 'status' => 'operational', 'uptime' => '99.98%', 'address' => '10.10.10.5'),
            array('name' => 'Database Cluster', 'status' => 'operational', 'uptime' => '99.95%', 'address' => '10.10.10.20'),
            array('name' => 'Mail Server', 'status' => 'degraded', 'uptime' => '98.20%', 'address' => '10.10.10.30'),
            array('name' => 'File Storage', 'status' => 'operational', 'uptime' => '99.99%', 'address' => '10.10.10.40'),
            array('name' => 'Admin Gateway', 'status' => 'operational', 'uptime' => '99.97%', 'address' => '10.10.10.1'),
            array('name' => 'Load Balancer (Primary)', 'status' => 'operational', 'uptime' => '100.00%', 'address' => '10.0.0.1'),
        );

        ?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>System Status - Acme Corp Intranet</title>
    <link rel="stylesheet" href="/assets/css/style.css">
</head>
<body>
    <nav class="navbar">
        <a href="/" class="brand">Acme Corp Intranet</a>
        <ul class="nav-links">
            <li><a href="/">Home</a></li>
            <li><a href="/about">About</a></li>
            <li><a href="/status" class="active">System Status</a></li>
            <li><a href="/admin">Admin</a></li>
        </ul>
    </nav>
    <div class="container">
        <div class="page-header">
            <h1>System Status</h1>
            <p>Current status of Acme Corp infrastructure services</p>
        </div>
        <div class="card">
            <h2>Service Health</h2>
            <table>
                <thead>
                    <tr>
                        <th>Service</th>
                        <th>Address</th>
                        <th>Status</th>
                        <th>Uptime (30d)</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($services as $svc): ?>
                    <tr>
                        <td><?php echo htmlspecialchars($svc['name']); ?></td>
                        <td><?php echo htmlspecialchars($svc['address']); ?></td>
                        <td>
                            <?php if ($svc['status'] === 'operational'): ?>
                                <span class="badge badge-success">Operational</span>
                            <?php elseif ($svc['status'] === 'degraded'): ?>
                                <span class="badge badge-warning">Degraded</span>
                            <?php else: ?>
                                <span class="badge badge-danger">Down</span>
                            <?php endif; ?>
                        </td>
                        <td><?php echo htmlspecialchars($svc['uptime']); ?></td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
        <div class="card">
            <h2>Recent Incidents</h2>
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Service</th>
                        <th>Description</th>
                        <th>Duration</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>2024-01-09</td>
                        <td>Mail Server</td>
                        <td>Intermittent delivery delays due to queue backlog</td>
                        <td>2h 15m</td>
                    </tr>
                    <tr>
                        <td>2024-01-03</td>
                        <td>Database Cluster</td>
                        <td>Planned maintenance - replica failover</td>
                        <td>45m</td>
                    </tr>
                    <tr>
                        <td>2023-12-28</td>
                        <td>Authentication Service</td>
                        <td>Certificate renewal caused brief outage</td>
                        <td>12m</td>
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
}
