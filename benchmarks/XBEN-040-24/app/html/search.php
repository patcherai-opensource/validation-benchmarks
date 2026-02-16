<?php
require_once 'includes/auth.php';
require_auth();

$search_type = isset($_GET['type']) ? $_GET['type'] : 'ipv4';
$allowed_types = ['ipv4', 'hardware'];
if (!in_array($search_type, $allowed_types)) {
    $search_type = 'ipv4';
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NetMon - Search</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="app-wrapper">
    <?php include 'includes/nav.php'; ?>
    
    <div class="main-content">
        <h1>Search</h1>
        
        <div class="search-tabs">
            <a href="search.php?type=ipv4" class="tab <?php echo $search_type === 'ipv4' ? 'tab-active' : ''; ?>">IPv4 Addresses</a>
            <a href="search.php?type=hardware" class="tab <?php echo $search_type === 'hardware' ? 'tab-active' : ''; ?>">Hardware Addresses</a>
        </div>
        
        <?php
        if ($search_type === 'ipv4') {
            include 'includes/search/ipv4.inc.php';
        } elseif ($search_type === 'hardware') {
            include 'includes/search/hardware.inc.php';
        }
        ?>
    </div>
</div>
</body>
</html>