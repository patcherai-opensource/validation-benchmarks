<?php
session_start();
if (!isset($_SESSION['logged_in'])) { header("Location: /admin/login.php"); exit; }
$pagename = ucfirst(basename(__FILE__, '.php'));
?>
<!DOCTYPE html>
<html><head><title>Dolibar ERP - <?php echo $pagename; ?></title>
<style>body{font-family:'Segoe UI',sans-serif;background:#f5f6fa;}.header{background:#1a1a2e;color:#fff;padding:15px 30px;}.header h1 span{color:#e94560;}.main{max-width:1000px;margin:40px auto;padding:30px;background:#fff;border-radius:8px;}h2{margin-bottom:20px;}.table{width:100%;border-collapse:collapse;}.table th,.table td{padding:12px;text-align:left;border-bottom:1px solid #ddd;}.table th{background:#f5f5f5;}</style>
</head><body>
<div class="header"><h1>Doli<span>bar</span> ERP</h1></div>
<div class="main">
<h2><?php echo $pagename; ?> Management</h2>
<table class="table">
<tr><th>ID</th><th>Name</th><th>Status</th><th>Actions</th></tr>
<tr><td>001</td><td>Sample Item 1</td><td>Active</td><td><a href="#">Edit</a></td></tr>
<tr><td>002</td><td>Sample Item 2</td><td>Active</td><td><a href="#">Edit</a></td></tr>
<tr><td>003</td><td>Sample Item 3</td><td>Inactive</td><td><a href="#">Edit</a></td></tr>
</table>
<p style="margin-top:20px;"><a href="/admin/index.php">Back to Dashboard</a></p>
</div>
</body></html>
