<?php
/**
 * Dolibarr ERP & CRM - Export Files Handler (API endpoint)
 * Version 12.0.3
 * 
 * JSON API endpoint for backup functionality
 */

session_start();

// Check if user is logged in and is admin
if (!isset($_SESSION['dolibarr_user']) || !isset($_SESSION['dolibarr_admin'])) {
    http_response_code(403);
    header('Content-Type: application/json');
    echo json_encode(['error' => 'Access denied. Please login first.']);
    exit;
}

header('Content-Type: application/json');

define('BACKUP_DIR', '/var/www/html/documents/backup');

function dol_sanitizeFileName($filename) {
    $filename = preg_replace('/[<>:"\\|?*]/', '', $filename);
    $filename = preg_replace('/[\x00-\x1f]/', '', $filename);
    $filename = str_replace([';', '|', '&'], '', $filename);
    return $filename;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $zipfilename_template = isset($_POST['zipfilename_template']) ? $_POST['zipfilename_template'] : 'backup';
    
    $sanitized_filename = dol_sanitizeFileName($zipfilename_template);
    
    if (!is_dir(BACKUP_DIR)) {
        mkdir(BACKUP_DIR, 0755, true);
    }
    
    $dummy_dir = '/var/www/html/documents/admin/temp';
    if (!is_dir($dummy_dir)) {
        mkdir($dummy_dir, 0755, true);
    }
    file_put_contents($dummy_dir . '/export_data.txt', 'Export data - ' . date('Y-m-d H:i:s'));
    
    $outputfile = BACKUP_DIR . '/' . $sanitized_filename . '.tar.gz';
    
    // VULNERABLE: Command injection possible
    $cmd = "tar -cvzf " . $outputfile . " -C /var/www/html/documents admin 2>&1";
    
    $output = array();
    $return_var = 0;
    exec($cmd, $output, $return_var);
    
    echo json_encode([
        'status' => $return_var === 0 ? 'success' : 'error',
        'message' => $return_var === 0 ? 'Backup created' : 'Backup failed',
        'output' => implode("\n", $output)
    ]);
    exit;
}

// GET request - list files in backup directory
$files = [];
if (is_dir(BACKUP_DIR)) {
    foreach (glob(BACKUP_DIR . '/*') as $file) {
        if (is_file($file)) {
            $files[] = [
                'name' => basename($file),
                'size' => filesize($file),
                'modified' => date('Y-m-d H:i:s', filemtime($file))
            ];
        }
    }
}

echo json_encode(['files' => $files]);
