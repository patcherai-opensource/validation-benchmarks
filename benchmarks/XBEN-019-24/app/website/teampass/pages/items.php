<?php
require_once __DIR__ . '/../includes/config/settings.php';

if (!isset($_SESSION['user_id'])) {
    header('Location: /login');
    exit;
}
?>
<!DOCTYPE html>
<html>
<head><title>TeamPass - Items</title></head>
<body>
<div id="items-container">
    <!-- Items loaded dynamically via AJAX -->
</div>
</body>
</html>
