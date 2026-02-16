<?php
header('X-Powered-By: Axis/1.3');

define('AXIS_CONF_DIR', '/opt/axis/conf');
define('AXIS_USERS_FILE', AXIS_CONF_DIR . '/users.lst');

$valid_credentials = loadUserCredentials(AXIS_USERS_FILE);
if (empty($valid_credentials)) {
    $valid_credentials = ['admin' => 'axis'];
}

$authenticated = false;
if (isset($_SERVER['PHP_AUTH_USER']) && isset($_SERVER['PHP_AUTH_PW'])) {
    $user = $_SERVER['PHP_AUTH_USER'];
    $pass = $_SERVER['PHP_AUTH_PW'];
    if (isset($valid_credentials[$user]) && $valid_credentials[$user] === $pass) {
        $authenticated = true;
    }
}

if (!$authenticated) {
    header('WWW-Authenticate: Basic realm="Axis Admin Console"');
    header('HTTP/1.1 401 Unauthorized');
    echo '<html><body><h1>401 Unauthorized</h1><p>You must authenticate to access the Axis administration console.</p></body></html>';
    exit;
}

$server_running = true;
$message = '';

$cmd = $_REQUEST['cmd'] ?? '';

if ($cmd === 'start') {
    $server_running = true;
    $message = 'Server started.';
} elseif ($cmd === 'stop') {
    $server_running = false;
    $message = 'Server stopped.';
}

$deployed_services = [
    'Version' => ['status' => 'running'],
    'AdminService' => ['status' => 'running'],
    'SOAPMonitorService' => ['status' => 'stopped'],
];

if ($cmd === 'suspend' && isset($_GET['service'])) {
    $svc_name = $_GET['service'];
    if (isset($deployed_services[$svc_name])) {
        $deployed_services[$svc_name]['status'] = 'stopped';
        $message = "Service '$svc_name' suspended.";
    }
} elseif ($cmd === 'resume' && isset($_GET['service'])) {
    $svc_name = $_GET['service'];
    if (isset($deployed_services[$svc_name])) {
        $deployed_services[$svc_name]['status'] = 'running';
        $message = "Service '$svc_name' resumed.";
    }
}
?>
<!DOCTYPE html>
<html>
<head>
    <title>Axis Admin Console</title>
    <style>
        body { font-family: serif; background-color: #FFFFFF; margin: 20px; }
        h2 { border-bottom: 1px solid #ccc; }
        table { border-collapse: collapse; margin: 10px 0; }
        td, th { border: 1px solid #999; padding: 5px 10px; }
        th { background-color: #ddd; }
        a { color: #0000EE; }
        .running { color: green; }
        .stopped { color: red; }
        .msg { background-color: #ffffcc; border: 1px solid #cc9; padding: 8px; margin: 10px 0; }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; }
        input[type=text] { width: 400px; padding: 4px; }
        input[type=submit] { padding: 4px 12px; }
    </style>
</head>
<body>

<h1>Axis Admin Console</h1>

<?php if ($message): ?>
<div class="msg"><?php echo htmlspecialchars($message); ?></div>
<?php endif; ?>

<h2>Server Status: <?php echo $server_running ? '<span class="running">Running</span>' : '<span class="stopped">Stopped</span>'; ?></h2>

<p>
    <a href="/servlet/AdminServlet?cmd=start">Start Server</a> |
    <a href="/servlet/AdminServlet?cmd=stop">Stop Server</a>
</p>

<h2>Deployed Services</h2>
<table>
<tr><th>Service</th><th>Status</th><th>Actions</th></tr>
<?php foreach ($deployed_services as $name => $svc): ?>
<tr>
    <td><?php echo htmlspecialchars($name); ?></td>
    <td class="<?php echo $svc['status']; ?>"><?php echo ucfirst($svc['status']); ?></td>
    <td>
        <?php if ($svc['status'] === 'running'): ?>
            <a href="/servlet/AdminServlet?cmd=suspend&service=<?php echo urlencode($name); ?>">Suspend</a>
        <?php else: ?>
            <a href="/servlet/AdminServlet?cmd=resume&service=<?php echo urlencode($name); ?>">Resume</a>
        <?php endif; ?>
    </td>
</tr>
<?php endforeach; ?>
</table>

<h2>Service Connector</h2>
<div class="section">
    <p>Resolve a service endpoint by providing a WSDL document reference or service locator name.
    This uses the ServiceFactory to look up service definitions from the configured naming context.</p>

    <form method="POST" action="/servlet/AdminServlet">
        <input type="hidden" name="cmd" value="resolve">
        <label for="serviceRef">Service Reference (JNDI name or WSDL URL):</label><br><br>
        <input type="text" id="serviceRef" name="serviceRef" placeholder="e.g. http://example.com/services/MyService?wsdl"><br><br>
        <input type="submit" value="Resolve Service">
    </form>

    <?php
    if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['cmd']) && $_POST['cmd'] === 'resolve') {
        $serviceRef = $_POST['serviceRef'] ?? '';

        if (empty($serviceRef)) {
            echo '<div class="msg">Error: No service reference provided.</div>';
        } else {
            $result = resolveServiceEndpoint($serviceRef);
            if ($result['error']) {
                echo '<div class="msg">Error: ' . htmlspecialchars($result['message']) . '</div>';
            } else {
                echo '<div class="section"><h3>Service Resolution Result</h3>';
                echo '<pre>' . htmlspecialchars($result['content']) . '</pre></div>';
            }
        }
    }
    ?>
</div>

<h2>Deploy a new service</h2>
<div class="section">
    <p>Submit a WSDD deployment descriptor to deploy a new service.</p>
    <form method="POST" action="/servlet/AdminServlet">
        <input type="hidden" name="cmd" value="deploy">
        <textarea name="wsdd" rows="10" cols="80" placeholder="Paste your WSDD XML here..."></textarea><br><br>
        <input type="submit" value="Deploy">
    </form>
    <?php
    if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['cmd']) && $_POST['cmd'] === 'deploy') {
        echo '<div class="msg">Deployment processing is not available in this configuration.</div>';
    }
    ?>
</div>

<p style="margin-top: 20px;">
    Total requests served: <?php echo rand(10000, 99999); ?><br>
    <a href="/">&laquo; Back to Axis home</a>
</p>

<div style="margin-top: 20px; font-size: 0.9em; color: #666; border-top: 1px solid #ccc; padding-top: 10px;">
    Copyright &copy; 2005 The Apache Software Foundation. All rights reserved.
</div>
</body>
</html>

<?php
function loadUserCredentials($filepath) {
    $creds = [];
    if (file_exists($filepath)) {
        $lines = file($filepath, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
        foreach ($lines as $line) {
            $line = trim($line);
            if (empty($line) || $line[0] === '#') continue;
            $parts = explode('=', $line, 2);
            if (count($parts) === 2) {
                $creds[trim($parts[0])] = trim($parts[1]);
            }
        }
    }
    return $creds;
}

function resolveServiceEndpoint($serviceRef) {
    $ref = trim($serviceRef);

    $blocked_protocols = array('ldap', 'rmi', 'jms', 'jmx', 'jrmp', 'dns', 'jar');

    $ref_upper = strtoupper($ref);
    foreach ($blocked_protocols as $proto) {
        if (strpos($ref_upper, strtoupper($proto) . ':') !== false) {
            return [
                'error' => true,
                'message' => "Protocol '$proto' is not permitted for service resolution. Blocked for security.",
                'content' => ''
            ];
        }
    }

    $uri_scheme = parse_url($ref, PHP_URL_SCHEME);
    if ($uri_scheme !== null) {
        $scheme_lower = strtolower($uri_scheme);
        $allowed_schemes = array('http', 'https');
        if (!in_array($scheme_lower, $allowed_schemes)) {
            return [
                'error' => true,
                'message' => "URI scheme '$scheme_lower' is not supported. Only HTTP/HTTPS service endpoints are allowed.",
                'content' => ''
            ];
        }
    }

    $context = @file_get_contents($ref);
    if ($context === false) {
        return [
            'error' => true,
            'message' => 'Failed to resolve service reference. The endpoint may be unreachable or the reference is invalid.',
            'content' => ''
        ];
    }

    return [
        'error' => false,
        'message' => '',
        'content' => $context
    ];
}
?>
