<?php
header('X-Powered-By: Axis/1.3');

function checkExtension($name, $required = true) {
    $loaded = extension_loaded($name);
    $status = $loaded ? 'OK' : ($required ? 'MISSING (CRITICAL)' : 'MISSING (Optional)');
    $color = $loaded ? 'green' : ($required ? 'red' : 'orange');
    return "<li style='color: $color'>$name - $status</li>";
}
?>
<!DOCTYPE html>
<html>
<head>
    <title>Axis - Happiness Page</title>
    <style>
        body { font-family: serif; background-color: #FFFFFF; margin: 20px; }
        h2 { border-bottom: 1px solid #ccc; }
        table { border-collapse: collapse; margin: 10px 0; }
        td { border: 1px solid #ccc; padding: 5px 10px; }
    </style>
</head>
<body>
<h1>Axis Happiness Page</h1>
<h2>Examining system configuration...</h2>

<h3>Needed Components</h3>
<ul>
<?php
echo checkExtension('curl', true);
echo checkExtension('xml', true);
echo checkExtension('json', true);
echo checkExtension('mbstring', true);
echo checkExtension('openssl', false);
?>
</ul>

<h3>Optional Components</h3>
<ul>
<?php
echo checkExtension('soap', false);
echo checkExtension('xmlrpc', false);
echo checkExtension('zip', false);
echo checkExtension('gd', false);
?>
</ul>

<?php
$needed = 0;
foreach (['curl', 'xml', 'json'] as $ext) {
    if (!extension_loaded($ext)) $needed++;
}
?>

<h3>
<?php if ($needed == 0): ?>
    The core Axis libraries are present. Axis should work.
<?php else: ?>
    <?php echo $needed; ?> critical component(s) missing. Axis may not work correctly.
<?php endif; ?>
</h3>

<h2>Examining Application Server</h2>
<table>
    <tr><td>PHP Version</td><td><?php echo PHP_VERSION; ?></td></tr>
    <tr><td>Server Software</td><td><?php echo $_SERVER['SERVER_SOFTWARE'] ?? 'Unknown'; ?></td></tr>
    <tr><td>Platform</td><td><?php echo PHP_OS; ?></td></tr>
</table>

<h2>Examining Axis Configuration</h2>
<table>
<?php
$conf_dir = '/opt/axis/conf';
$attachments_dir = '/opt/axis/attachments';
$conf_exists = is_dir($conf_dir);
$att_exists = is_dir($attachments_dir);
?>
    <tr>
        <td>Configuration Directory</td>
        <td><?php echo htmlspecialchars($conf_dir); ?></td>
        <td style="color: <?php echo $conf_exists ? 'green' : 'red'; ?>"><?php echo $conf_exists ? 'Found' : 'Missing'; ?></td>
    </tr>
    <tr>
        <td>Attachments Directory</td>
        <td><?php echo htmlspecialchars($attachments_dir); ?></td>
        <td style="color: <?php echo $att_exists ? 'green' : 'red'; ?>"><?php echo $att_exists ? 'Found' : 'Missing'; ?></td>
    </tr>
</table>

<div style="margin-top: 40px; font-size: 0.9em; color: #666; border-top: 1px solid #ccc; padding-top: 10px;">
    Copyright &copy; 2005 The Apache Software Foundation. All rights reserved.
</div>
</body>
</html>
