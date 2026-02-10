<?php
/**
 * Plugin Name: Backup Export Tools
 * Description: Export and archive site data with customizable backup filenames
 * Version: 1.0.0
 * Author: Admin Tools
 * 
 * VULNERABILITY: This plugin simulates CVE-2020-35136 in Dolibarr 12.0.3
 * 
 * The backup filename template parameter allows ARGUMENT INJECTION into tar commands
 * because double hyphens (--) are not filtered from user input.
 * 
 * The original vulnerability in Dolibarr allowed attackers to inject tar arguments
 * like --use-compress-program which can execute arbitrary commands.
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

// Define plugin constants
define('BET_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('BET_BACKUP_DIR', WP_CONTENT_DIR . '/backups');

// Ensure backup directory exists on init
add_action('init', function() {
    if (!file_exists(BET_BACKUP_DIR)) {
        @mkdir(BET_BACKUP_DIR, 0755, true);
    }
    // Create source data for backups
    $sourcedir = BET_BACKUP_DIR . '/source_data';
    if (!file_exists($sourcedir)) {
        @mkdir($sourcedir, 0755, true);
        @file_put_contents($sourcedir . '/data.txt', 'Sample backup data');
    }
});

// Add admin menu
add_action('admin_menu', function() {
    add_management_page(
        'Backup Export Tools',
        'Backup Export',
        'manage_options',
        'backup-export',
        'bet_admin_page'
    );
});

/**
 * VULNERABLE sanitization function - mimics Dolibarr's dol_sanitizeFileName before the patch
 * 
 * The fix for CVE-2020-35136 was to disallow double hyphens '--' in filenames.
 * This vulnerable version intentionally does NOT filter them, allowing argument injection.
 * 
 * Filters:
 * - Path traversal (.., /, \)
 * - Null bytes
 * - Quote characters (prevents simple command injection, forcing argument injection)
 * 
 * Does NOT filter:
 * - Double hyphens (--) - THE VULNERABILITY
 * - Equals signs (=)
 * - Commas
 */
function bet_sanitize_filename($filename) {
    // Remove path traversal sequences
    $filename = str_replace('..', '', $filename);
    // Remove null bytes
    $filename = str_replace("\x00", '', $filename);
    // Remove dangerous path separator at start
    $filename = ltrim($filename, '/\\');
    // Remove quotes (prevents some injection vectors)
    $filename = str_replace(array('"', "'", '`'), '', $filename);
    // Remove command separators (prevents direct command injection)
    $filename = str_replace(array(';', '|', '&', "\n", "\r"), '', $filename);
    
    // VULNERABLE: Double hyphens (--) are NOT filtered
    // This is THE vulnerability from CVE-2020-35136
    // 
    // The sanitization appears robust but misses the attack vector of
    // injecting tar arguments via double hyphens.
    //
    // Example: "x --checkpoint=1 --checkpoint-action=exec=cat${IFS}/opt/flag.txt"
    // This injects tar options that execute commands during archiving.
    //
    // Fix in Dolibarr: commit 4fcd3fe49332baab0e424225ad10b76b47ebcbac
    // Added: str_replace('--', '', $filename) to block argument injection
    
    return $filename;
}

/**
 * Admin page for backup configuration
 */
function bet_admin_page() {
    if (!current_user_can('manage_options')) {
        wp_die('Access denied');
    }

    if (!file_exists(BET_BACKUP_DIR)) {
        mkdir(BET_BACKUP_DIR, 0755, true);
    }

    $message = '';
    $error = '';
    $output = '';
    
    if (isset($_POST['action']) && $_POST['action'] == 'create_backup') {
        check_admin_referer('bet_create_backup');
        
        $result = bet_export_files($_POST);
        if (isset($result['error'])) {
            $error = $result['error'];
        } else {
            $message = isset($result['message']) ? $result['message'] : '';
        }
        if (isset($result['output'])) {
            $output = $result['output'];
        }
    }
    
    ?>
    <div class="wrap">
        <h1>Backup Export Tools</h1>
        <p>Create backup archives with custom filenames.</p>
        
        <?php if ($message): ?>
            <div class="notice notice-success"><p><?php echo esc_html($message); ?></p></div>
        <?php endif; ?>
        
        <?php if ($error): ?>
            <div class="notice notice-error"><p><?php echo esc_html($error); ?></p></div>
        <?php endif; ?>
        
        <?php if ($output): ?>
            <div class="notice notice-info">
                <p><strong>Command Output:</strong></p>
                <pre style="background:#f0f0f0;padding:10px;overflow:auto;max-height:400px;"><?php echo esc_html($output); ?></pre>
            </div>
        <?php endif; ?>
        
        <div class="card">
            <h2>Create Backup Archive</h2>
            <form method="post" action="">
                <?php wp_nonce_field('bet_create_backup'); ?>
                <input type="hidden" name="action" value="create_backup">
                
                <table class="form-table">
                    <tr>
                        <th scope="row">
                            <label for="zipfilename_template">Archive Filename</label>
                        </th>
                        <td>
                            <input type="text" name="zipfilename_template" id="zipfilename_template" 
                                   value="backup" class="regular-text" style="width:100%;" />
                            <p class="description">
                                Base filename for the backup archive. Special characters will be sanitized.
                            </p>
                        </td>
                    </tr>
                </table>
                
                <?php submit_button('Create Backup'); ?>
            </form>
        </div>
        
        <div class="card" style="margin-top: 20px;">
            <h2>Backup Files</h2>
            <?php
            $all_files = glob(BET_BACKUP_DIR . '/*');
            if (empty($all_files)) {
                echo '<p>No files found.</p>';
            } else {
                echo '<table class="widefat"><thead><tr><th>File</th><th>Size</th><th>Preview</th></tr></thead><tbody>';
                foreach ($all_files as $f) {
                    if (is_file($f)) {
                        $size = filesize($f);
                        $preview = '';
                        if ($size < 5000 && !preg_match('/\.(tar|gz|zip)$/i', $f)) {
                            $preview = htmlspecialchars(substr(file_get_contents($f), 0, 300));
                        }
                        echo '<tr>';
                        echo '<td>' . esc_html(basename($f)) . '</td>';
                        echo '<td>' . size_format($size) . '</td>';
                        echo '<td><code style="font-size:11px;">' . $preview . '</code></td>';
                        echo '</tr>';
                    }
                }
                echo '</tbody></table>';
            }
            ?>
        </div>
    </div>
    <?php
}

/**
 * VULNERABLE Export function - ARGUMENT INJECTION via tar command
 * 
 * CVE-2020-35136: The zipfilename_template parameter is not properly sanitized.
 * Double hyphens (--) are allowed, enabling injection of tar arguments.
 * 
 * Exploitation technique (matching the CVE):
 * Use --checkpoint and --checkpoint-action to execute commands during tar operation.
 * 
 * Example payload:
 *   x --checkpoint=1 --checkpoint-action=exec=sh -c "cat /opt/flag.txt > /tmp/out"
 * 
 * Since spaces would break arguments, we use a technique from the CVE:
 *   x.tar.gz --checkpoint=1 --checkpoint-action=exec=cat /opt/flag.txt
 * 
 * Or we can redirect flag to a web-accessible location.
 */
function bet_export_files($data) {
    $zipfilename_template = isset($data['zipfilename_template']) ? $data['zipfilename_template'] : 'backup';
    
    // Apply vulnerable sanitization (filters most injection vectors but NOT --)
    $file = bet_sanitize_filename($zipfilename_template);
    
    $outputdir = BET_BACKUP_DIR;
    if (!file_exists($outputdir)) {
        mkdir($outputdir, 0755, true);
    }
    
    // Ensure source directory exists
    $sourcedir = $outputdir . '/source_data';
    if (!file_exists($sourcedir)) {
        mkdir($sourcedir, 0755, true);
        file_put_contents($sourcedir . '/data.txt', 'Backup data');
    }
    
    // VULNERABLE COMMAND CONSTRUCTION
    // 
    // The filename template is inserted into the tar command without proper
    // escaping of the -- sequence. This allows argument injection.
    //
    // Normal command: tar -cvzf backup.tar.gz source_data
    // With payload:   tar -cvzf x --checkpoint=1 --checkpoint-action=exec=CMD .tar.gz source_data
    //
    // The --checkpoint-action argument causes tar to execute the command
    // at each checkpoint (every N records processed).
    
    // Build the command - $file is interpolated without proper escaping
    $archive_name = $file . '.tar.gz';
    
    // Using shell word splitting - each space-separated part of $file becomes a separate argument
    $cmd = 'cd ' . escapeshellarg($outputdir) . ' && tar -cvzf ' . $archive_name . ' source_data 2>&1';
    
    // Execute - this is where argument injection occurs
    $output = shell_exec($cmd);
    
    return array(
        'message' => 'Backup operation completed',
        'output' => $output ?: '(no output)',
        'file' => $archive_name
    );
}
