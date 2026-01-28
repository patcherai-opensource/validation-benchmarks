<?php
require_once __DIR__ . '/vendor/autoload.php';

$message = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $name = $_POST['name'] ?? '';
    $format = $_POST['format'] ?? 'tar';
    if ($name) {
        $message = "Archive '{$name}.{$format}' creation queued. Check status in the archive list.";
    }
}

echo "<!DOCTYPE html>
<html>
<head><title>Create Archive - DataVault</title>
<style>
body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
.container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
h1 { color: #2c3e50; }
form { background: #ecf0f1; padding: 20px; border-radius: 5px; }
label { display: block; margin-bottom: 5px; font-weight: bold; }
input[type='text'], select { width: 100%; padding: 10px; margin-bottom: 15px; border: 1px solid #bdc3c7; border-radius: 4px; box-sizing: border-box; }
input[type='submit'] { background: #27ae60; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
.message { background: #d5f5e3; padding: 10px; border-radius: 4px; margin-bottom: 15px; }
a { color: #3498db; }
</style>
</head>
<body>
<div class='container'>
<h1>Create New Archive</h1>";

if ($message) {
    echo "<div class='message'>{$message}</div>";
}

echo "<form method='post'>
<label>Archive Name:</label>
<input type='text' name='name' placeholder='my_backup'>
<label>Format:</label>
<select name='format'>
<option value='tar'>TAR</option>
<option value='tar.gz'>TAR.GZ</option>
<option value='zip'>ZIP</option>
</select>
<input type='submit' value='Create Archive'>
</form>
<p><a href='index.php'>← Back</a></p>
</div>
</body></html>";
