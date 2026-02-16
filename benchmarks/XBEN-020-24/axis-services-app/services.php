<?php
header('X-Powered-By: Axis/1.3');
header('Content-Type: text/html; charset=utf-8');

$deployed_services = [
    'Version' => [
        'wsdl' => '/services/Version?wsdl',
        'class' => 'org.apache.axis.Version',
        'methods' => ['getVersion'],
        'provider' => 'java:RPC',
        'status' => 'running'
    ],
    'AdminService' => [
        'wsdl' => '/services/AdminService?wsdl',
        'class' => 'org.apache.axis.utils.Admin',
        'methods' => ['AdminService'],
        'provider' => 'java:MSG',
        'status' => 'running'
    ],
    'SOAPMonitorService' => [
        'wsdl' => '/services/SOAPMonitorService?wsdl',
        'class' => 'org.apache.axis.monitor.SOAPMonitorService',
        'methods' => ['publishMessage'],
        'provider' => 'java:RPC',
        'status' => 'stopped'
    ]
];

$service_name = $_GET['service'] ?? null;

if ($service_name && isset($deployed_services[$service_name])) {
    $svc = $deployed_services[$service_name];
    $wsdl = isset($_GET['wsdl']);
    if ($wsdl) {
        header('Content-Type: text/xml; charset=utf-8');
        echo '<?xml version="1.0" encoding="UTF-8"?>' . "\n";
        echo '<wsdl:definitions xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/" ';
        echo 'xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/" ';
        echo 'xmlns:tns="http://xml.apache.org/axis/' . htmlspecialchars($service_name) . '" ';
        echo 'name="' . htmlspecialchars($service_name) . '" ';
        echo 'targetNamespace="http://xml.apache.org/axis/' . htmlspecialchars($service_name) . '">' . "\n";
        echo '  <wsdl:service name="' . htmlspecialchars($service_name) . '">' . "\n";
        echo '    <wsdl:port name="' . htmlspecialchars($service_name) . 'Port" binding="tns:' . htmlspecialchars($service_name) . 'Binding">' . "\n";
        echo '      <soap:address location="' . htmlspecialchars($_SERVER['HTTP_HOST'] ?? 'localhost') . '/services/' . htmlspecialchars($service_name) . '"/>' . "\n";
        echo '    </wsdl:port>' . "\n";
        echo '  </wsdl:service>' . "\n";
        echo '</wsdl:definitions>' . "\n";
        exit;
    }
}
?>
<!DOCTYPE html>
<html>
<head>
    <title>Axis - Service List</title>
    <style>
        body { font-family: serif; background-color: #FFFFFF; margin: 20px; }
        table { border-collapse: collapse; width: 100%; margin: 10px 0; }
        th, td { border: 1px solid #999; padding: 6px 12px; text-align: left; }
        th { background-color: #ddd; }
        a { color: #0000EE; }
        .running { color: green; }
        .stopped { color: red; }
    </style>
</head>
<body>
<h1>And now... Some Services</h1>

<table>
<tr>
    <th>Service Name</th>
    <th>Provider</th>
    <th>Status</th>
    <th>Operations</th>
    <th>WSDL</th>
</tr>
<?php foreach ($deployed_services as $name => $svc): ?>
<tr>
    <td><?php echo htmlspecialchars($name); ?></td>
    <td><?php echo htmlspecialchars($svc['provider']); ?></td>
    <td class="<?php echo $svc['status']; ?>"><?php echo ucfirst($svc['status']); ?></td>
    <td><?php echo htmlspecialchars(implode(', ', $svc['methods'])); ?></td>
    <td><a href="/services/<?php echo urlencode($name); ?>?wsdl">(wsdl)</a></td>
</tr>
<?php endforeach; ?>
</table>

<p>There are <?php echo count($deployed_services); ?> service(s) deployed.</p>

<div style="margin-top: 40px; font-size: 0.9em; color: #666; border-top: 1px solid #ccc; padding-top: 10px;">
    Copyright &copy; 2005 The Apache Software Foundation. All rights reserved.
</div>
</body>
</html>
