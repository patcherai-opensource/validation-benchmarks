<?php
/**
 * Documents directory browser
 * Allows viewing and downloading backup files
 */

session_start();

// Check if user is logged in
if (!isset($_SESSION['dolibarr_user'])) {
    header('Location: /?error=access_denied');
    exit;
}

$base_path = '/var/www/html/documents';
$current_path = isset($_GET['path']) ? $_GET['path'] : '/';

// Sanitize path to prevent directory traversal outside documents
$current_path = '/' . ltrim($current_path, '/');
$current_path = str_replace('..', '', $current_path);
$full_path = realpath($base_path . $current_path);

// Ensure we stay within documents directory
if ($full_path === false || strpos($full_path, $base_path) !== 0) {
    $full_path = $base_path;
    $current_path = '/';
}

// Handle file download
if (isset($_GET['download'])) {
    $file = basename($_GET['download']);
    $file_path = $full_path . '/' . $file;
    
    if (file_exists($file_path) && is_file($file_path) && strpos(realpath($file_path), $base_path) === 0) {
        header('Content-Type: application/octet-stream');
        header('Content-Disposition: attachment; filename="' . $file . '"');
        header('Content-Length: ' . filesize($file_path));
        readfile($file_path);
        exit;
    }
}

// Handle file view
if (isset($_GET['view'])) {
    $file = basename($_GET['view']);
    $file_path = $full_path . '/' . $file;
    
    if (file_exists($file_path) && is_file($file_path) && strpos(realpath($file_path), $base_path) === 0) {
        header('Content-Type: text/plain');
        readfile($file_path);
        exit;
    }
}

?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Documents - Dolibarr ERP/CRM 12.0.3</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 15px 20px; }
        .header h1 { font-size: 24px; }
        .nav { background: #34495e; padding: 10px 20px; }
        .nav a { color: #ecf0f1; text-decoration: none; margin-right: 20px; padding: 5px 10px; }
        .nav a:hover { background: #2c3e50; border-radius: 3px; }
        .container { max-width: 1200px; margin: 30px auto; padding: 0 20px; }
        .card { background: white; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); padding: 25px; margin-bottom: 20px; }
        .card h2 { color: #2c3e50; margin-bottom: 15px; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        .breadcrumb { background: #ecf0f1; padding: 10px 15px; border-radius: 4px; margin-bottom: 20px; }
        .breadcrumb a { color: #3498db; text-decoration: none; }
        .file-list { list-style: none; }
        .file-list li { padding: 10px 15px; border-bottom: 1px solid #eee; display: flex; align-items: center; }
        .file-list li:hover { background: #f8f9fa; }
        .file-list a { text-decoration: none; color: #2c3e50; flex: 1; }
        .file-list .icon { margin-right: 10px; }
        .file-list .actions { margin-left: auto; }
        .file-list .actions a { margin-left: 10px; color: #3498db; font-size: 12px; }
        .file-size { color: #7f8c8d; font-size: 12px; margin-left: 10px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Dolibarr ERP/CRM - Documents</h1>
    </div>

    <div class="nav">
        <a href="/">Home</a>
        <a href="/admin/">Admin Tools</a>
        <a href="/admin/tools/dolibarr_export.php">Backup</a>
        <a href="/documents/">Documents</a>
    </div>

    <div class="container">
        <div class="card">
            <h2>File Browser</h2>
            
            <div class="breadcrumb">
                Current Path: <a href="/documents/">/documents</a><?php 
                    $parts = explode('/', trim($current_path, '/'));
                    $build_path = '';
                    foreach ($parts as $part) {
                        if ($part) {
                            $build_path .= '/' . $part;
                            echo ' / <a href="/documents/?path=' . urlencode($build_path) . '">' . htmlspecialchars($part) . '</a>';
                        }
                    }
                ?>
            </div>

            <ul class="file-list">
                <?php if ($current_path !== '/'): ?>
                <li>
                    <span class="icon">📁</span>
                    <a href="/documents/?path=<?php echo urlencode(dirname($current_path)); ?>">..</a>
                </li>
                <?php endif; ?>
                
                <?php
                $items = scandir($full_path);
                foreach ($items as $item) {
                    if ($item === '.' || $item === '..') continue;
                    
                    $item_path = $full_path . '/' . $item;
                    $is_dir = is_dir($item_path);
                    $size = $is_dir ? '' : round(filesize($item_path) / 1024, 2) . ' KB';
                    
                    if ($is_dir) {
                        echo '<li>';
                        echo '<span class="icon">📁</span>';
                        echo '<a href="/documents/?path=' . urlencode($current_path . '/' . $item) . '">' . htmlspecialchars($item) . '</a>';
                        echo '</li>';
                    } else {
                        echo '<li>';
                        echo '<span class="icon">📄</span>';
                        echo '<a href="#">' . htmlspecialchars($item) . '</a>';
                        echo '<span class="file-size">' . $size . '</span>';
                        echo '<span class="actions">';
                        echo '<a href="/documents/?path=' . urlencode($current_path) . '&view=' . urlencode($item) . '" target="_blank">View</a>';
                        echo '<a href="/documents/?path=' . urlencode($current_path) . '&download=' . urlencode($item) . '">Download</a>';
                        echo '</span>';
                        echo '</li>';
                    }
                }
                ?>
            </ul>
        </div>
    </div>
</body>
</html>
