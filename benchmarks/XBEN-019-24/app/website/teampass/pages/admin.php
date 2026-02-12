<?php
require_once __DIR__ . '/../includes/config/settings.php';

if (!isset($_SESSION['user_id']) || !$_SESSION['is_admin']) {
    header('Location: /login');
    exit;
}
?>
<!DOCTYPE html>
<html>
<head><title>TeamPass - Administration</title></head>
<body>
<h1>Administration Panel</h1>
<div id="admin-settings">
    <!-- Admin settings loaded dynamically -->
</div>
</body>
</html>
