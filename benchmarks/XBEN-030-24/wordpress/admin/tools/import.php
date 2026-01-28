<?php
session_start();
if (!isset($_SESSION['logged_in'])) { header("Location: /admin/login.php"); exit; }
?>
<!DOCTYPE html>
<html><head><title>Dolibar ERP - Import</title>
<style>body{font-family:'Segoe UI',sans-serif;background:#f5f6fa;}.header{background:#1a1a2e;color:#fff;padding:15px 30px;}.header h1 span{color:#e94560;}.main{max-width:800px;margin:40px auto;padding:30px;background:#fff;border-radius:8px;}h2{margin-bottom:20px;}</style>
</head><body>
<div class="header"><h1>Doli<span>bar</span> ERP</h1></div>
<div class="main">
<h2>Import Data</h2>
<p>File upload functionality is currently disabled for security reasons.</p>
<p><a href="/admin/tools/">Back to Admin Tools</a></p>
</div>
</body></html>
