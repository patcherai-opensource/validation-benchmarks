<?php
require_once dirname(__FILE__) . '/../lib/ServiceFactory.php';

header('X-Powered-By: Axis/1.3');

$factory = ServiceFactory::getInstance();
$services = $factory->listServices();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Axis - Deployed Services</title>
    <style>
        body { font-family: Arial, Helvetica, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border: 1px solid #ccc; }
        h1 { color: #336699; border-bottom: 2px solid #336699; padding-bottom: 10px; }
        .nav { background: #336699; padding: 10px; margin: -20px -20px 20px -20px; }
        .nav a { color: white; text-decoration: none; margin-right: 15px; font-weight: bold; }
        .nav a:hover { text-decoration: underline; }
        table { border-collapse: collapse; width: 100%; }
        td, th { border: 1px solid #ccc; padding: 8px; text-align: left; }
        th { background: #336699; color: white; }
        a { color: #336699; }
        .info { background: #eef4ff; border: 1px solid #99c; padding: 10px; margin: 10px 0; }
    </style>
</head>
<body>
<div class="container">
    <div class="nav">
        <a href="/">Home</a>
        <a href="/axis/services/listServices.php">View Services</a>
        <a href="/axis/admin/">Administration</a>
    </div>

    <h1>Deployed Web Services</h1>
    
    <div class="info">
        <p>The following web services are deployed on this Axis server:</p>
    </div>

    <table>
        <tr>
            <th>Service Name</th>
            <th>Endpoint</th>
            <th>Status</th>
            <th>Type</th>
        </tr>
        <?php foreach ($services as $svc): ?>
        <tr>
            <td><strong><?php echo htmlspecialchars($svc['name']); ?></strong></td>
            <td><?php echo htmlspecialchars($svc['endpoint']); ?></td>
            <td><?php echo htmlspecialchars($svc['status']); ?></td>
            <td><?php echo htmlspecialchars($svc['type']); ?></td>
        </tr>
        <?php endforeach; ?>
    </table>

    <p style="margin-top: 20px;">Total services: <strong><?php echo count($services); ?></strong></p>

    <hr>
    <p style="font-size: 11px; color: #999;">Copyright &copy; 2000-2006 Apache Software Foundation. All Rights Reserved.</p>
</div>
</body>
</html>
