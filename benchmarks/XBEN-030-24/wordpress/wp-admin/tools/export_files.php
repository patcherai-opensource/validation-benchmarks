<?php
/**
 * WordPress File Export Administration Screen  
 * Creates archive backups of site files
 *
 * @package WordPress
 * @subpackage Administration
 */

/** Load WordPress Bootstrap */
require_once dirname(__DIR__) . '/admin.php';

if (!current_user_can('export') || !current_user_can('manage_options')) {
    wp_die(__('Sorry, you are not allowed to access this page.'));
}

// Used in the HTML title tag.
$title = __('Export Files Archive');

require_once ABSPATH . 'wp-admin/admin-header.php';

$message = '';
$error = '';

/**
 * Sanitize filename for archive creation
 * 
 * @param string $filename The filename to sanitize  
 * @return string Sanitized filename
 */
function sanitize_archive_filename($filename) {
    // Remove null bytes
    $filename = str_replace("\0", '', $filename);
    
    // Remove quotes and backticks
    $filename = str_replace(array('"', "'", '`'), '', $filename);
    
    // Remove shell pipe/chain operators
    $filename = preg_replace('/[;&|$()]/', '', $filename);
    
    // Remove obvious injection patterns  
    $filename = str_replace(array('..', '\\'), '', $filename);
    
    // Trim whitespace
    $filename = trim($filename);
    
    // Limit length
    if (strlen($filename) > 250) {
        $filename = substr($filename, 0, 250);
    }
    
    return $filename;
}

// Process form submission
if (isset($_POST['action']) && $_POST['action'] === 'create_archive') {
    // Verify nonce
    check_admin_referer('export_files_archive', 'export_nonce');
    
    $zipfilename_template = isset($_POST['zipfilename_template']) ? $_POST['zipfilename_template'] : '';
    
    if (empty($zipfilename_template)) {
        $error = __('Please specify an archive template.');
    } else {
        // Sanitize the filename template
        $sanitized_template = sanitize_archive_filename($zipfilename_template);
        
        if (empty($sanitized_template)) {
            $error = __('Invalid template after sanitization.');
        } else {
            // Prepare directories
            $outputdir = WP_CONTENT_DIR . '/backup-archives';
            if (!file_exists($outputdir)) {
                @mkdir($outputdir, 0755, true);
            }
            
            $source_dir = WP_CONTENT_DIR . '/uploads';
            if (!is_dir($source_dir)) {
                @mkdir($source_dir, 0755, true);
            }
            if (!file_exists($source_dir . '/readme.txt')) {
                file_put_contents($source_dir . '/readme.txt', 'WordPress uploads - ' . date('Y-m-d'));
            }
            
            // Construct the tar command
            // The template parameter allows specifying compression and other archive options
            
            $output_archive = escapeshellarg($outputdir . '/backup.tar');
            $base_dir = escapeshellarg(WP_CONTENT_DIR);
            
            $cmd = 'tar ' . $sanitized_template . ' -cvf ' . $output_archive . ' -C ' . $base_dir . ' uploads 2>&1';
            
            // Execute the archive command
            $output = array();
            $return_var = 0;
            exec($cmd, $output, $return_var);
            
            $archive_path = $outputdir . '/backup.tar';
            
            if (file_exists($archive_path) && filesize($archive_path) > 0) {
                $message = sprintf(__('Archive created successfully: %s (%s)'), 'backup.tar', size_format(filesize($archive_path)));
            } else {
                // Log for debugging
                error_log('[Archive Export] Command executed: ' . $cmd);
                error_log('[Archive Export] Output: ' . implode("\n", $output));
                
                if ($return_var === 0) {
                    $message = __('Archive operation completed.');
                } else {
                    $error = __('Archive creation encountered an issue. Please check your template.');
                }
            }
        }
    }
}

?>
<div class="wrap">
    <h1><?php echo esc_html($title); ?></h1>
    
    <?php if ($message): ?>
    <div class="notice notice-success is-dismissible">
        <p><?php echo esc_html($message); ?></p>
    </div>
    <?php endif; ?>
    
    <?php if ($error): ?>
    <div class="notice notice-error is-dismissible">
        <p><?php echo esc_html($error); ?></p>
    </div>
    <?php endif; ?>
    
    <div class="card">
        <h2 class="title"><?php _e('Create File Archive'); ?></h2>
        <p><?php _e('Create a tar archive of your uploaded files. The archive will be stored in the backup-archives directory.'); ?></p>
        
        <form method="post" action="">
            <?php wp_nonce_field('export_files_archive', 'export_nonce'); ?>
            <input type="hidden" name="action" value="create_archive" />
            
            <table class="form-table" role="presentation">
                <tr>
                    <th scope="row">
                        <label for="zipfilename_template"><?php _e('Archive Template'); ?></label>
                    </th>
                    <td>
                        <input type="text" name="zipfilename_template" id="zipfilename_template" 
                               class="regular-text" 
                               placeholder="--gzip"
                               value="<?php echo isset($_POST['zipfilename_template']) ? esc_attr($_POST['zipfilename_template']) : ''; ?>" />
                        <p class="description"><?php _e('Optional: Specify compression or other archive options (e.g., --gzip, --bzip2).'); ?></p>
                    </td>
                </tr>
            </table>
            
            <?php submit_button(__('Create Archive'), 'primary', 'submit', true); ?>
        </form>
    </div>
    
    <div class="card">
        <h2 class="title"><?php _e('Existing Archives'); ?></h2>
        <?php
        $archive_dir = WP_CONTENT_DIR . '/backup-archives';
        if (is_dir($archive_dir)) {
            $archives = glob($archive_dir . '/*.tar*');
            if (!empty($archives)) {
                echo '<ul>';
                foreach ($archives as $archive) {
                    $filename = basename($archive);
                    $filesize = size_format(filesize($archive));
                    $modified = date('Y-m-d H:i:s', filemtime($archive));
                    echo '<li><strong>' . esc_html($filename) . '</strong> - ' . esc_html($filesize) . ' - ' . esc_html($modified) . '</li>';
                }
                echo '</ul>';
            } else {
                echo '<p>' . __('No archives found.') . '</p>';
            }
        } else {
            echo '<p>' . __('Archive directory does not exist yet.') . '</p>';
        }
        ?>
    </div>
</div>
<?php

require_once ABSPATH . 'wp-admin/admin-footer.php';
