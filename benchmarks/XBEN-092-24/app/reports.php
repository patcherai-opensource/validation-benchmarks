<?php
require_once __DIR__ . '/vendor/autoload.php';

$loader = new \Twig\Loader\FilesystemLoader(__DIR__ . '/templates');
$twig = new \Twig\Environment($loader);

$reports = [
    ['id' => 'RPT001', 'name' => 'Monthly Storage Usage', 'date' => '2024-01-31'],
    ['id' => 'RPT002', 'name' => 'Archive Access Logs', 'date' => '2024-01-30'],
    ['id' => 'RPT003', 'name' => 'Extraction Statistics', 'date' => '2024-01-28'],
];

echo "<!DOCTYPE html>
<html>
<head><title>Reports - DataVault</title>
<style>
body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
.container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
h1 { color: #2c3e50; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 10px; border-bottom: 1px solid #ddd; text-align: left; }
th { background: #3498db; color: white; }
a { color: #3498db; }
</style>
</head>
<body>
<div class='container'>
<h1>System Reports</h1>
<table>
<tr><th>Report ID</th><th>Name</th><th>Date</th><th>Action</th></tr>";

foreach ($reports as $r) {
    echo "<tr><td>{$r['id']}</td><td>{$r['name']}</td><td>{$r['date']}</td><td><a href='#'>Download PDF</a></td></tr>";
}

echo "</table>
<p><a href='index.php'>← Back</a></p>
</div>
</body></html>";
