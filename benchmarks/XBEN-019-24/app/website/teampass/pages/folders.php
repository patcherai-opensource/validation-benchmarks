<?php
require_once __DIR__ . '/../includes/config/settings.php';

if (!isset($_SESSION['user_id'])) {
    header('Location: /login');
    exit;
}
?>
<!DOCTYPE html>
<html>
<head><title>TeamPass - Folders</title></head>
<body>
<div id="folders-tree">
    <!-- Folder tree loaded via AJAX -->
</div>
</body>
</html>
