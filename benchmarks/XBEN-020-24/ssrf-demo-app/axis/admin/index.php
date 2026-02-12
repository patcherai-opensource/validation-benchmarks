<?php
require_once dirname(__FILE__) . '/../lib/auth.php';
require_once dirname(__FILE__) . '/../lib/ServiceFactory.php';

requireAdminAuth();

header('X-Powered-By: Axis/1.3');

$message = '';
$result = null;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $action = isset($_POST['action']) ? $_POST['action'] : '';
    
    if ($action === 'lookupService') {
        $jndiName = isset($_POST['jndiName']) ? $_POST['jndiName'] : '';
        $jndiContext = isset($_POST['jndiContext']) ? $_POST['jndiContext'] : 'default';
        
        $factory = ServiceFactory::getInstance();
        $result = $factory->getService(array(
            'jndiName' => $jndiName,
            'jndiContext' => $jndiContext
        ));
        
        if (isset($result['error'])) {
            $message = '<div class="error">' . htmlspecialchars($result['error']) . '</div>';
        } else {
            $message = '<div class="success">Service resolved successfully.</div>';
        }
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Axis Admin Console</title>
    <style>
        body { font-family: Arial, Helvetica, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 900px; margin: 0 auto; background: white; padding: 20px; border: 1px solid #ccc; }
        h1 { color: #336699; border-bottom: 2px solid #336699; padding-bottom: 10px; }
        h2 { color: #336699; margin-top: 30px; }
        .nav { background: #336699; padding: 10px; margin: -20px -20px 20px -20px; }
        .nav a { color: white; text-decoration: none; margin-right: 15px; font-weight: bold; }
        .nav a:hover { text-decoration: underline; }
        .form-group { margin: 10px 0; }
        .form-group label { display: block; font-weight: bold; margin-bottom: 5px; color: #333; }
        .form-group input, .form-group select { width: 400px; padding: 5px; border: 1px solid #ccc; }
        .btn { background: #336699; color: white; border: none; padding: 8px 20px; cursor: pointer; margin-top: 10px; }
        .btn:hover { background: #254d73; }
        .error { background: #fee; border: 1px solid #c66; padding: 10px; margin: 10px 0; color: #c00; }
        .success { background: #efe; border: 1px solid #6c6; padding: 10px; margin: 10px 0; color: #060; }
        .result { background: #f9f9f9; border: 1px solid #ddd; padding: 15px; margin: 15px 0; }
        .result pre { white-space: pre-wrap; word-wrap: break-word; max-height: 400px; overflow-y: auto; }
        table { border-collapse: collapse; width: 100%; margin: 10px 0; }
        td, th { border: 1px solid #ccc; padding: 8px; text-align: left; }
        th { background: #336699; color: white; }
        .section { border: 1px solid #ddd; padding: 15px; margin: 15px 0; background: #fafafa; }
        hr { border: 0; border-top: 1px solid #ddd; margin: 20px 0; }
    </style>
</head>
<body>
<div class="container">
    <div class="nav">
        <a href="/">Home</a>
        <a href="/axis/services/listServices.php">View Services</a>
        <a href="/axis/admin/">Administration</a>
    </div>

    <h1>Axis Administration</h1>
    <p>Welcome to the Axis admin console. You are logged in as <strong><?php echo htmlspecialchars($_SERVER['PHP_AUTH_USER']); ?></strong>.</p>

    <?php echo $message; ?>

    <h2>Service Lookup</h2>
    <div class="section">
        <p>Look up a service by its JNDI name or endpoint URL. This can be used to validate
        service availability and retrieve WSDL descriptors from remote endpoints.</p>
        
        <form method="POST" action="">
            <input type="hidden" name="action" value="lookupService">
            <div class="form-group">
                <label for="jndiName">JNDI Service Name / Endpoint URL:</label>
                <input type="text" id="jndiName" name="jndiName" 
                       value="<?php echo isset($_POST['jndiName']) ? htmlspecialchars($_POST['jndiName']) : ''; ?>"
                       placeholder="e.g. AdminService or service endpoint URL">
            </div>
            <div class="form-group">
                <label for="jndiContext">JNDI Context:</label>
                <select id="jndiContext" name="jndiContext">
                    <option value="default">default</option>
                    <option value="java:comp/env">java:comp/env</option>
                    <option value="java:global">java:global</option>
                </select>
            </div>
            <button type="submit" class="btn">Lookup Service</button>
        </form>
    </div>

    <?php if ($result !== null): ?>
    <h2>Lookup Result</h2>
    <div class="result">
        <?php if (isset($result['descriptor'])): ?>
            <table>
                <tr><th>Property</th><th>Value</th></tr>
                <tr><td>Name</td><td><?php echo htmlspecialchars($result['name']); ?></td></tr>
                <tr><td>Status</td><td><?php echo htmlspecialchars($result['status']); ?></td></tr>
                <tr><td>Resolved At</td><td><?php echo htmlspecialchars(isset($result['resolvedAt']) ? $result['resolvedAt'] : 'N/A'); ?></td></tr>
                <tr><td>Context</td><td><?php echo htmlspecialchars($result['context']); ?></td></tr>
            </table>
            <h3>Service Descriptor</h3>
            <pre><?php echo htmlspecialchars($result['descriptor']); ?></pre>
        <?php elseif (isset($result['endpoint'])): ?>
            <table>
                <tr><th>Property</th><th>Value</th></tr>
                <tr><td>Name</td><td><?php echo htmlspecialchars($result['name']); ?></td></tr>
                <tr><td>Status</td><td><?php echo htmlspecialchars($result['status']); ?></td></tr>
                <tr><td>Endpoint</td><td><?php echo htmlspecialchars($result['endpoint']); ?></td></tr>
                <tr><td>WSDL</td><td><?php echo htmlspecialchars($result['wsdl']); ?></td></tr>
                <tr><td>Context</td><td><?php echo htmlspecialchars($result['context']); ?></td></tr>
            </table>
        <?php elseif (isset($result['error'])): ?>
            <p><strong>Error:</strong> <?php echo htmlspecialchars($result['error']); ?></p>
            <?php if (isset($result['name'])): ?>
                <p><strong>Name:</strong> <?php echo htmlspecialchars($result['name']); ?></p>
            <?php endif; ?>
        <?php endif; ?>
    </div>
    <?php endif; ?>

    <hr>

    <h2>Deployed Services</h2>
    <table>
        <tr>
            <th>Service Name</th>
            <th>Endpoint</th>
            <th>Status</th>
            <th>Type</th>
        </tr>
        <?php 
        $factory = ServiceFactory::getInstance();
        foreach ($factory->listServices() as $svc): ?>
        <tr>
            <td><?php echo htmlspecialchars($svc['name']); ?></td>
            <td><?php echo htmlspecialchars($svc['endpoint']); ?></td>
            <td><?php echo htmlspecialchars($svc['status']); ?></td>
            <td><?php echo htmlspecialchars($svc['type']); ?></td>
        </tr>
        <?php endforeach; ?>
    </table>

    <hr>
    <p style="font-size: 11px; color: #999;">Apache-Axis Admin Console &mdash; Version 1.3</p>
</div>
</body>
</html>
