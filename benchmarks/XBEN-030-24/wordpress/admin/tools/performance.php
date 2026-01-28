<?php
session_start();
if (!isset($_SESSION['logged_in'])) { header("Location: /admin/login.php"); exit; }
?>
<!DOCTYPE html>
<html><head><title>Dolibar ERP - Performance</title>
<style>body{font-family:'Segoe UI',sans-serif;background:#f5f6fa;}.header{background:#1a1a2e;color:#fff;padding:15px 30px;}.header h1 span{color:#e94560;}.main{max-width:800px;margin:40px auto;padding:30px;background:#fff;border-radius:8px;}h2{margin-bottom:20px;}.stat{background:#f5f5f5;padding:15px;margin:10px 0;border-radius:4px;}</style>
</head><body>
<div class="header"><h1>Doli<span>bar</span> ERP</h1></div>
<div class="main">
<h2>Performance Metrics</h2>
<div class="stat"><strong>Memory Usage:</strong> 45.2 MB / 256 MB</div>
<div class="stat"><strong>CPU Load:</strong> 12%</div>
<div class="stat"><strong>Database Queries:</strong> 142 queries</div>
<div class="stat"><strong>Cache Hit Ratio:</strong> 87%</div>
<p style="margin-top:20px;"><a href="/admin/tools/">Back to Admin Tools</a></p>
</div>
</body></html>
