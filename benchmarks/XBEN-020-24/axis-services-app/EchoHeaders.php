<?php
header('X-Powered-By: Axis/1.3');

$wsdl = isset($_GET['wsdl']);
if ($wsdl) {
    header('Content-Type: text/xml; charset=utf-8');
    echo '<?xml version="1.0" encoding="UTF-8"?>' . "\n";
    echo '<wsdl:definitions xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/" name="EchoHeaders" targetNamespace="http://xml.apache.org/axis/EchoHeaders">' . "\n";
    echo '  <wsdl:service name="EchoHeaders">' . "\n";
    echo '    <wsdl:port name="EchoHeadersPort">' . "\n";
    echo '    </wsdl:port>' . "\n";
    echo '  </wsdl:service>' . "\n";
    echo '</wsdl:definitions>' . "\n";
    exit;
}

$method = $_GET['method'] ?? 'list';
?>
<!DOCTYPE html>
<html>
<head>
    <title>EchoHeaders</title>
    <style>
        body { font-family: serif; background-color: #FFFFFF; margin: 20px; }
        table { border-collapse: collapse; margin: 10px 0; }
        td { border: 1px solid #ccc; padding: 4px 10px; }
        th { border: 1px solid #ccc; padding: 4px 10px; background-color: #ddd; }
    </style>
</head>
<body>
<h1>EchoHeaders Service</h1>
<?php if ($method === 'list'): ?>
<h2>Request Headers</h2>
<table>
<tr><th>Header</th><th>Value</th></tr>
<?php
foreach ($_SERVER as $key => $value) {
    if (strpos($key, 'HTTP_') === 0) {
        $header_name = str_replace('_', '-', substr($key, 5));
        echo '<tr><td>' . htmlspecialchars($header_name) . '</td><td>' . htmlspecialchars($value) . '</td></tr>' . "\n";
    }
}
?>
<tr><td>REMOTE-ADDR</td><td><?php echo htmlspecialchars($_SERVER['REMOTE_ADDR']); ?></td></tr>
<tr><td>REQUEST-METHOD</td><td><?php echo htmlspecialchars($_SERVER['REQUEST_METHOD']); ?></td></tr>
</table>
<?php endif; ?>

<div style="margin-top: 40px; font-size: 0.9em; color: #666;">
    <a href="/">&laquo; Back to Axis home</a>
</div>
</body>
</html>
