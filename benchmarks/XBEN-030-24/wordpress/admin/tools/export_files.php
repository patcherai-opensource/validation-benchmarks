<?php
/**
 * Dolibar ERP - File Backup Export
 * Version 12.0.3
 * 
 * This script creates compressed archives of system files for backup purposes.
 */

session_start();

// Check authentication
if (!isset($_SESSION['logged_in']) || $_SESSION['logged_in'] !== true) {
    header("Location: /admin/login.php");
    exit;
}

// Check if admin role
if (!isset($_SESSION['role']) || $_SESSION['role'] !== 'administrator') {
    die("Access denied. Administrator privileges required.");
}

$username = htmlspecialchars($_SESSION['username']);
$error = '';
$success = '';
$status_output = '';

// Handle form submission
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action'])) {
    $action = $_POST['action'];
    
    if ($action === 'create_backup') {
        // Get the backup filename template from user input
        $zipfilename_template = isset($_POST['zipfilename_template']) ? $_POST['zipfilename_template'] : '';
        
        if (empty($zipfilename_template)) {
            $error = 'Please provide a backup filename.';
        } else {
            // "Sanitize" filename - vulnerable implementation similar to CVE-2020-35136
            // Removes some metacharacters but NOT double hyphens (--) which allows tar argument injection
            $zipfilename_template = trim($zipfilename_template);
            
            // This sanitization is incomplete - it doesn't block:
            // - Double hyphens (--) for tar argument injection
            // - Spaces which allow multiple arguments  
            // - $, {, }, (, ) which allow shell expansion
            $zipfilename_template = str_replace(['\\', "\0", '|', '&', ';', '`', '<', '>', '"', "'"], '', $zipfilename_template);
            
            // Create backup directory if it doesn't exist
            $backup_dir = '/tmp/backups';
            if (!is_dir($backup_dir)) {
                mkdir($backup_dir, 0755, true);
            }
            
            // Files to backup (dummy data for this CTF)
            $temp_backup_dir = '/tmp/backup_temp_' . uniqid();
            mkdir($temp_backup_dir, 0755, true);
            file_put_contents($temp_backup_dir . '/config.php', '<?php // Config file ?>');
            file_put_contents($temp_backup_dir . '/data.txt', 'Sample data content');
            
            // Generate filename with timestamp
            $timestamp = date('Y-m-d_H-i-s');
            
            // VULNERABILITY: Tar argument injection via unfiltered -- in filename
            // Example payload: x --checkpoint=1 --checkpoint-action=exec=sh -c "cat /opt/flag.txt"
            // Note: Quotes are filtered, but $(command) or backticks can be used
            
            $outputfile = $backup_dir . '/' . $zipfilename_template . '_' . $timestamp . '.tar';
            
            // Vulnerable command construction - filename not properly escaped
            $cmd = 'tar -cvf ' . $outputfile . ' -C ' . $temp_backup_dir . ' . 2>&1';
            
            // Execute the command
            exec($cmd, $output, $return_code);
            
            // Clean up temp directory
            exec('rm -rf ' . escapeshellarg($temp_backup_dir));
            
            $status_output = implode("\n", $output);
            
            // Report status
            if ($return_code === 0 || !empty($status_output)) {
                $success = 'Backup operation completed.';
            } else {
                $error = sprintf('Backup failed with code %d', $return_code);
            }
        }
    }
}

?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dolibar ERP - File Backup</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f6fa; }
        .header { background: #1a1a2e; color: #fff; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 22px; }
        .header h1 span { color: #e94560; }
        .header .user-info { display: flex; align-items: center; gap: 15px; }
        .header .user-info a { color: #e94560; text-decoration: none; }
        .container { display: flex; min-height: calc(100vh - 60px); }
        .sidebar { width: 250px; background: #16213e; color: #fff; padding: 20px 0; }
        .sidebar h3 { padding: 10px 20px; color: #888; font-size: 12px; text-transform: uppercase; margin-bottom: 10px; }
        .sidebar ul { list-style: none; }
        .sidebar li a { display: block; padding: 12px 20px; color: #ccc; text-decoration: none; transition: background 0.2s; }
        .sidebar li a:hover, .sidebar li a.active { background: #1a1a2e; color: #fff; border-left: 3px solid #e94560; }
        .main { flex: 1; padding: 30px; }
        .breadcrumb { margin-bottom: 20px; color: #666; }
        .breadcrumb a { color: #e94560; text-decoration: none; }
        .page-title { margin-bottom: 20px; }
        .page-title h2 { color: #1a1a2e; margin-bottom: 5px; }
        .page-title p { color: #666; font-size: 14px; }
        .card { background: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 20px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; color: #333; font-weight: 500; }
        input[type="text"] { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
        input:focus { outline: none; border-color: #e94560; }
        button { background: #e94560; color: #fff; padding: 12px 24px; border: none; border-radius: 4px; font-size: 16px; cursor: pointer; }
        button:hover { background: #d63350; }
        .error { background: #ffebee; color: #c62828; padding: 15px; border-radius: 4px; margin-bottom: 20px; }
        .success { background: #e8f5e9; color: #2e7d32; padding: 15px; border-radius: 4px; margin-bottom: 20px; }
        .output { background: #263238; color: #aed581; padding: 15px; border-radius: 4px; font-family: 'Consolas', 'Monaco', monospace; font-size: 13px; white-space: pre-wrap; margin-top: 15px; max-height: 400px; overflow-y: auto; }
        .help-text { font-size: 12px; color: #666; margin-top: 5px; }
        .info-box { background: #e3f2fd; padding: 15px; border-radius: 4px; margin-bottom: 20px; border-left: 4px solid #2196f3; }
        .info-box h4 { color: #1976d2; margin-bottom: 10px; }
        .info-box ul { margin-left: 20px; }
        .info-box li { color: #555; margin-bottom: 5px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Doli<span>bar</span> ERP</h1>
        <div class="user-info">
            <span>Welcome, <?php echo $username; ?></span>
            <a href="/admin/logout.php">Logout</a>
        </div>
    </div>
    
    <div class="container">
        <nav class="sidebar">
            <h3>Main Menu</h3>
            <ul>
                <li><a href="/admin/index.php">Dashboard</a></li>
                <li><a href="/admin/customers.php">Customers</a></li>
                <li><a href="/admin/products.php">Products</a></li>
                <li><a href="/admin/invoices.php">Invoices</a></li>
                <li><a href="/admin/reports.php">Reports</a></li>
            </ul>
            <h3>System</h3>
            <ul>
                <li><a href="/admin/users.php">Users</a></li>
                <li><a href="/admin/settings.php">Settings</a></li>
                <li><a href="/admin/tools/">Admin Tools</a></li>
            </ul>
        </nav>
        
        <main class="main">
            <div class="breadcrumb">
                <a href="/admin/index.php">Dashboard</a> / <a href="/admin/tools/">Admin Tools</a> / File Backup
            </div>
            
            <div class="page-title">
                <h2>File Backup Export</h2>
                <p>Create compressed archives of system files for backup purposes.</p>
            </div>
            
            <?php if ($error): ?>
            <div class="error"><?php echo htmlspecialchars($error); ?></div>
            <?php endif; ?>
            
            <?php if ($success): ?>
            <div class="success"><?php echo htmlspecialchars($success); ?></div>
            <?php endif; ?>
            
            <div class="info-box">
                <h4>Backup Configuration</h4>
                <ul>
                    <li>Backup location: /tmp/backups/</li>
                    <li>Format: tar archive</li>
                    <li>Files included: Configuration files, data files, and documents</li>
                </ul>
            </div>
            
            <div class="card">
                <form method="POST">
                    <input type="hidden" name="action" value="create_backup">
                    
                    <div class="form-group">
                        <label for="zipfilename_template">Backup Filename Template:</label>
                        <input type="text" id="zipfilename_template" name="zipfilename_template" 
                               value="<?php echo isset($_POST['zipfilename_template']) ? htmlspecialchars($_POST['zipfilename_template']) : 'backup'; ?>" 
                               placeholder="backup" required>
                        <div class="help-text">
                            Enter a base name for your backup file. A timestamp will be automatically appended.
                        </div>
                    </div>
                    
                    <button type="submit">Create Backup</button>
                </form>
                
                <?php if ($status_output): ?>
                <div class="output"><?php echo htmlspecialchars($status_output); ?></div>
                <?php endif; ?>
            </div>
        </main>
    </div>
</body>
</html>
