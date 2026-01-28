<?php
session_start();
if (!isset($_SESSION['logged_in'])) { header("Location: /admin/login.php"); exit; }
$message = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') { $message = 'Cache cleared successfully (simulated).'; }
?>
<!DOCTYPE html>
<html><head><title>Dolibar ERP - Cache</title>
<style>body{font-family:'Segoe UI',sans-serif;background:#f5f6fa;}.header{background:#1a1a2e;color:#fff;padding:15px 30px;}.header h1 span{color:#e94560;}.main{max-width:800px;margin:40px auto;padding:30px;background:#fff;border-radius:8px;}h2{margin-bottom:20px;}button{background:#e94560;color:#fff;border:none;padding:12px 24px;border-radius:4px;cursor:pointer;}.msg{background:#e8f5e9;padding:15px;border-radius:4px;margin-bottom:20px;}</style>
</head><body>
<div class="header"><h1>Doli<span>bar</span> ERP</h1></div>
<div class="main">
<h2>Cache Management</h2>
<?php if ($message): ?><div class="msg"><?php echo $message; ?></div><?php endif; ?>
<form method="POST"><button type="submit">Clear Cache</button></form>
<p style="margin-top:20px;"><a href="/admin/tools/">Back to Admin Tools</a></p>
</div>
</body></html>
