<?php
session_start();
if (!isset($_SESSION['logged_in'])) { header("Location: /admin/login.php"); exit; }
?>
<!DOCTYPE html>
<html><head><title>Dolibar ERP - System Logs</title>
<style>body{font-family:'Segoe UI',sans-serif;background:#f5f6fa;}.header{background:#1a1a2e;color:#fff;padding:15px 30px;}.header h1 span{color:#e94560;}.main{max-width:800px;margin:40px auto;padding:30px;background:#fff;border-radius:8px;}h2{margin-bottom:20px;}.log{background:#263238;color:#aed581;padding:15px;font-family:monospace;font-size:12px;}</style>
</head><body>
<div class="header"><h1>Doli<span>bar</span> ERP</h1></div>
<div class="main">
<h2>System Logs</h2>
<div class="log">
[2024-01-28 10:15:32] INFO: User admin logged in successfully
[2024-01-28 10:16:45] INFO: Dashboard accessed
[2024-01-28 10:18:22] INFO: Admin tools page accessed
[2024-01-28 10:22:11] INFO: Backup process initiated
[2024-01-28 10:22:15] INFO: Backup completed successfully
</div>
<p style="margin-top:20px;"><a href="/admin/tools/">Back to Admin Tools</a></p>
</div>
</body></html>
