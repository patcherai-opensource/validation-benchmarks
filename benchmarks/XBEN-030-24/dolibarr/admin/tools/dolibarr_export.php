<?php
/**
 * Dolibarr ERP & CRM - Backup / Export
 * Version 12.0.3
 * 
 * VULNERABILITY: CVE-2020-35136 - Command injection via zipfilename_template
 * The filename parameter allows injection of shell commands through backticks or $()
 * due to insufficient sanitization.
 */

session_start();

// Check if user is logged in and is admin
if (!isset($_SESSION['dolibarr_user']) || !isset($_SESSION['dolibarr_admin'])) {
    header('Location: /?error=access_denied');
    exit;
}

$message = '';
$error = '';
$backup_result = '';

// Define backup directory
define('BACKUP_DIR', '/var/www/html/documents/backup');

/**
 * Sanitize filename - VULNERABLE VERSION
 * This mimics the pre-patch Dolibarr function that had insufficient filtering
 */
function dol_sanitizeFileName($filename) {
    // Remove some dangerous characters
    // VULNERABILITY: Does not filter backticks ` or $() which allow command substitution
    $filename = preg_replace('/[<>:"\\|?*]/', '', $filename);
    $filename = preg_replace('/[\x00-\x1f]/', '', $filename);
    // Also filter semicolons and pipes for basic protection, but not enough!
    $filename = str_replace([';', '|', '&'], '', $filename);
    return $filename;
}

// Handle backup request
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action']) && $_POST['action'] === 'backup') {
    $zipfilename_template = isset($_POST['zipfilename_template']) ? $_POST['zipfilename_template'] : 'backup';
    
    // Apply vulnerable sanitization
    $sanitized_filename = dol_sanitizeFileName($zipfilename_template);
    
    // Create backup output directory if it doesn't exist
    if (!is_dir(BACKUP_DIR)) {
        mkdir(BACKUP_DIR, 0755, true);
    }
    
    // Create a dummy file to backup
    $dummy_dir = '/var/www/html/documents/admin/temp';
    if (!is_dir($dummy_dir)) {
        mkdir($dummy_dir, 0755, true);
    }
    file_put_contents($dummy_dir . '/export_data.txt', 'Dolibarr export data - ' . date('Y-m-d H:i:s'));
    
    // VULNERABLE COMMAND CONSTRUCTION
    // The filename is embedded in the command WITHOUT proper escaping
    // Command substitution via backticks or $() will be executed
    // Example payload: backup_$(cat /opt/flag.txt > /var/www/html/documents/backup/flag.txt)
    
    $outputfile = BACKUP_DIR . '/' . $sanitized_filename . '.tar.gz';
    
    // VULNERABLE: Filename embedded directly without escapeshellarg()
    $cmd = "tar -cvzf " . $outputfile . " -C /var/www/html/documents admin 2>&1";
    
    // Execute the command
    $output = array();
    $return_var = 0;
    exec($cmd, $output, $return_var);
    
    $backup_result = implode("\n", $output);
    
    // Check for any file that looks like an output file
    $created_files = glob(BACKUP_DIR . '/*.tar.gz');
    
    if ($return_var === 0 || count($created_files) > 0) {
        $message = "Backup process completed!";
    } else {
        $error = "Backup process encountered issues.";
    }
}

?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Backup / Export - Dolibarr ERP/CRM 12.0.3</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 24px; }
        .header .version { font-size: 12px; color: #95a5a6; }
        .nav { background: #34495e; padding: 10px 20px; }
        .nav a { color: #ecf0f1; text-decoration: none; margin-right: 20px; padding: 5px 10px; }
        .nav a:hover, .nav a.active { background: #2c3e50; border-radius: 3px; }
        .container { max-width: 1200px; margin: 30px auto; padding: 0 20px; }
        .card { background: white; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); padding: 25px; margin-bottom: 20px; }
        .card h2 { color: #2c3e50; margin-bottom: 15px; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        .btn { display: inline-block; background: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; border: none; cursor: pointer; font-size: 14px; }
        .btn:hover { background: #2980b9; }
        .btn-success { background: #27ae60; }
        .btn-success:hover { background: #219a52; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; color: #2c3e50; font-weight: 500; }
        .form-group input, .form-group select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
        .form-group small { color: #7f8c8d; font-size: 12px; margin-top: 5px; display: block; }
        .alert { padding: 15px; border-radius: 4px; margin-bottom: 20px; }
        .alert-danger { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .alert-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .output-box { background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 4px; font-family: monospace; font-size: 13px; max-height: 300px; overflow-y: auto; white-space: pre-wrap; word-wrap: break-word; }
        .footer { text-align: center; padding: 20px; color: #7f8c8d; font-size: 12px; }
        .info-table { width: 100%; border-collapse: collapse; }
        .info-table td { padding: 8px; border-bottom: 1px solid #eee; }
        .info-table td:first-child { font-weight: 500; color: #2c3e50; width: 200px; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>Dolibarr ERP/CRM</h1>
            <span class="version">Version 12.0.3</span>
        </div>
        <div>
            Welcome, <strong><?php echo htmlspecialchars($_SESSION['dolibarr_user']); ?></strong> |
            <a href="/?logout=1" style="color: #e74c3c;">Logout</a>
        </div>
    </div>

    <div class="nav">
        <a href="/">Home</a>
        <a href="/admin/">Admin Tools</a>
        <a href="/admin/tools/dolibarr_export.php" class="active">Backup</a>
        <a href="/documents/">Documents</a>
    </div>

    <div class="container">
        <?php if ($message): ?>
        <div class="alert alert-success"><?php echo htmlspecialchars($message); ?></div>
        <?php endif; ?>
        
        <?php if ($error): ?>
        <div class="alert alert-danger"><?php echo $error; ?></div>
        <?php endif; ?>

        <div class="card">
            <h2>Backup / Export Files</h2>
            <p style="margin-bottom: 20px;">Create a compressed archive of your Dolibarr documents folder.</p>
            
            <form method="POST" action="">
                <input type="hidden" name="action" value="backup">
                
                <div class="form-group">
                    <label for="zipfilename_template">Archive Filename Template</label>
                    <input type="text" id="zipfilename_template" name="zipfilename_template" value="backup_dolibarr_<?php echo date('Ymd'); ?>" placeholder="Enter backup filename">
                    <small>The archive will be saved as [filename].tar.gz in the documents/backup directory.</small>
                </div>
                
                <div class="form-group">
                    <label for="backup_type">Backup Type</label>
                    <select id="backup_type" name="backup_type">
                        <option value="files">Files only</option>
                        <option value="database">Database only</option>
                        <option value="all">Files and Database</option>
                    </select>
                </div>
                
                <button type="submit" class="btn btn-success">Generate Backup</button>
            </form>
        </div>

        <?php if ($backup_result): ?>
        <div class="card">
            <h2>Backup Output</h2>
            <div class="output-box"><?php echo htmlspecialchars($backup_result); ?></div>
        </div>
        <?php endif; ?>

        <div class="card">
            <h2>System Information</h2>
            <table class="info-table">
                <tr>
                    <td>Backup Directory</td>
                    <td><?php echo BACKUP_DIR; ?></td>
                </tr>
                <tr>
                    <td>Current Date</td>
                    <td><?php echo date('Y-m-d H:i:s'); ?></td>
                </tr>
                <tr>
                    <td>PHP Version</td>
                    <td><?php echo phpversion(); ?></td>
                </tr>
                <tr>
                    <td>Web Server</td>
                    <td><?php echo $_SERVER['SERVER_SOFTWARE']; ?></td>
                </tr>
            </table>
        </div>

        <div class="card">
            <h2>Recent Files in Backup Directory</h2>
            <?php
            $all_files = glob(BACKUP_DIR . '/*');
            $backup_files = array_filter($all_files, 'is_file');
            if ($backup_files && count($backup_files) > 0):
            ?>
            <table class="info-table">
                <?php foreach ($backup_files as $backup): ?>
                <tr>
                    <td><?php echo htmlspecialchars(basename($backup)); ?></td>
                    <td><?php echo date('Y-m-d H:i:s', filemtime($backup)); ?></td>
                    <td><?php echo round(filesize($backup) / 1024, 2); ?> KB</td>
                    <td><a href="/documents/?path=/backup&view=<?php echo urlencode(basename($backup)); ?>" target="_blank">View</a></td>
                </tr>
                <?php endforeach; ?>
            </table>
            <?php else: ?>
            <p style="color: #7f8c8d;">No files found in backup directory.</p>
            <?php endif; ?>
        </div>
    </div>

    <div class="footer">
        <p>Dolibarr ERP/CRM 12.0.3 - Open Source Software</p>
    </div>
</body>
</html>
