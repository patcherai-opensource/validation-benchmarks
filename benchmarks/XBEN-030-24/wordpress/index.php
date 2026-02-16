<?php

require 'includes/session.php';
require_once 'includes/functions.php';
ensureCSRFSessionToken();
require_once 'includes/config.php';
require_once 'includes/authenticate.php';

$page = $_GET['p'] ?? 'dashboard';

$validPages = [
    'dashboard' => 'Dashboard',
    'network_conf' => 'Networking',
    'tunnel_conf' => 'Tunnel',
    'system_info' => 'System',
    'about' => 'About',
];

if (!array_key_exists($page, $validPages)) {
    $page = 'dashboard';
}

$uptime = @shell_exec('uptime -p') ?: 'unknown';
$hostname = @gethostname() ?: 'netgate';
$meminfo = @file_get_contents('/proc/meminfo');
$memTotal = 0;
$memAvail = 0;
if ($meminfo) {
    preg_match('/MemTotal:\s+(\d+)/', $meminfo, $m);
    $memTotal = isset($m[1]) ? intval($m[1]) * 1024 : 0;
    preg_match('/MemAvailable:\s+(\d+)/', $meminfo, $m);
    $memAvail = isset($m[1]) ? intval($m[1]) * 1024 : 0;
}
$memUsedPct = $memTotal > 0 ? round(($memTotal - $memAvail) / $memTotal * 100, 1) : 0;

?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <?php echo CSRFMetaTag(); ?>
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title><?php echo NETCFG_BRAND_TEXT; ?> - <?php echo $validPages[$page]; ?></title>
    <link href="app/css/style.css" rel="stylesheet">
</head>
<body>
    <div id="wrapper">
        <nav id="sidebar">
            <div class="sidebar-brand"><?php echo NETCFG_BRAND_TEXT; ?></div>
            <ul class="nav-list">
                <li><a href="?p=dashboard" class="<?php echo $page === 'dashboard' ? 'active' : ''; ?>">&#9678; Dashboard</a></li>
                <?php if (NETCFG_NETWORK_ENABLED): ?>
                <li><a href="?p=network_conf" class="<?php echo $page === 'network_conf' ? 'active' : ''; ?>">&#9741; Networking</a></li>
                <?php endif; ?>
                <?php if (NETCFG_TUNNEL_ENABLED): ?>
                <li><a href="?p=tunnel_conf" class="<?php echo $page === 'tunnel_conf' ? 'active' : ''; ?>">&#128274; Tunnel</a></li>
                <?php endif; ?>
                <?php if (NETCFG_SYSTEM_ENABLED): ?>
                <li><a href="?p=system_info" class="<?php echo $page === 'system_info' ? 'active' : ''; ?>">&#9881; System</a></li>
                <?php endif; ?>
                <li><a href="?p=about" class="<?php echo $page === 'about' ? 'active' : ''; ?>">&#9432; About</a></li>
            </ul>
            <div class="sidebar-footer">
                <div>Memory: <?php echo $memUsedPct; ?>%</div>
                <div><?php echo htmlspecialchars(trim($uptime)); ?></div>
            </div>
        </nav>
        <div id="content">
            <div class="topbar">
                <span class="hostname"><?php echo htmlspecialchars($hostname); ?></span>
                <span class="version">v<?php echo NETCFG_VERSION; ?></span>
            </div>
            <div class="container">
                <?php echo renderTemplate($page, [
                    'memTotal' => $memTotal,
                    'memAvail' => $memAvail,
                    'memUsedPct' => $memUsedPct,
                    'uptime' => $uptime,
                    'hostname' => $hostname,
                ]); ?>
            </div>
        </div>
    </div>
    <script src="app/js/app.js"></script>
</body>
</html>
