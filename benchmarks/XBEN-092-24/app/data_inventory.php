<?php
require_once __DIR__ . '/vendor/autoload.php';

$inventory = [
    ['category' => 'Documents', 'count' => 1523, 'size' => '2.3 GB'],
    ['category' => 'Archives', 'count' => 89, 'size' => '15.7 GB'],
    ['category' => 'Backups', 'count' => 42, 'size' => '128.4 GB'],
    ['category' => 'Logs', 'count' => 4521, 'size' => '890 MB'],
];

echo "<!DOCTYPE html>
<html>
<head><title>Data Inventory - DataVault</title>
<style>
body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
.container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
h1 { color: #2c3e50; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 10px; border-bottom: 1px solid #ddd; text-align: left; }
th { background: #27ae60; color: white; }
a { color: #3498db; }
.total { font-weight: bold; background: #ecf0f1; }
</style>
</head>
<body>
<div class='container'>
<h1>Data Inventory</h1>
<table>
<tr><th>Category</th><th>Item Count</th><th>Total Size</th></tr>";

foreach ($inventory as $item) {
    echo "<tr><td>{$item['category']}</td><td>{$item['count']}</td><td>{$item['size']}</td></tr>";
}

echo "<tr class='total'><td>Total</td><td>6175</td><td>147.3 GB</td></tr>
</table>
<p><a href='index.php'>← Back</a></p>
</div>
</body></html>";
