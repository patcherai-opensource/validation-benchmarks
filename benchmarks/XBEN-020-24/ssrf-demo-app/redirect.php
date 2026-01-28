<?php
// Legacy redirect handler - kept for backwards compatibility
header('HTTP/1.1 301 Moved Permanently');
header('Location: /');
exit;
?>
