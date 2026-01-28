<?php
// Legacy endpoint - redirects to widget viewer
header('HTTP/1.1 301 Moved Permanently');
header('Location: /widget.php?id=' . urlencode($_GET['id'] ?? 'data-viz'));
exit;
?>
