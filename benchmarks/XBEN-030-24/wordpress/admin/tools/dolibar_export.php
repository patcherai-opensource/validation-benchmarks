<?php
/**
 * Dolibar ERP - Database Export
 * This is a SAFE (non-vulnerable) page that properly escapes inputs
 */

session_start();

if (!isset($_SESSION['logged_in']) || $_SESSION['logged_in'] !== true) {
    header("Location: /admin/login.php");
    exit;
}

$username = htmlspecialchars($_SESSION['username']);
$message = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $table = isset($_POST['table']) ? $_POST['table'] : 'all';
    // This is properly sanitized
    $table = preg_replace('/[^a-zA-Z0-9_]/', '', $table);
    $message = 'Database export initiated for table: ' . htmlspecialchars($table) . ' (simulated)';
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Dolibar ERP - Database Export</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: #f5f6fa; }
        .header { background: #1a1a2e; color: #fff; padding: 15px 30px; }
        .header h1 span { color: #e94560; }
        .main { max-width: 800px; margin: 40px auto; padding: 30px; background: #fff; border-radius: 8px; }
        h2 { margin-bottom: 20px; color: #1a1a2e; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; }
        select, button { padding: 12px; font-size: 14px; }
        select { width: 100%; border: 1px solid #ddd; border-radius: 4px; }
        button { background: #e94560; color: #fff; border: none; border-radius: 4px; cursor: pointer; }
        .message { background: #e8f5e9; padding: 15px; border-radius: 4px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="header"><h1>Doli<span>bar</span> ERP</h1></div>
    <div class="main">
        <h2>Database Export</h2>
        <?php if ($message): ?>
        <div class="message"><?php echo $message; ?></div>
        <?php endif; ?>
        <form method="POST">
            <div class="form-group">
                <label>Select Table:</label>
                <select name="table">
                    <option value="all">All Tables</option>
                    <option value="customers">Customers</option>
                    <option value="products">Products</option>
                    <option value="invoices">Invoices</option>
                </select>
            </div>
            <button type="submit">Export Database</button>
        </form>
    </div>
</body>
</html>
