<?php
/**
 * Git Plugin Installer Class
 * 
 * Handles the installation of WordPress plugins from Git repositories.
 * This mimics the Saltcorn vulnerability where plugin names are used
 * unsafely in shell commands.
 */

if (!defined('ABSPATH')) {
    exit;
}

class GPI_Installer {
    
    private $temp_dir;
    private $plugins_dir;
    
    public function __construct() {
        $this->temp_dir = WP_CONTENT_DIR . '/gpi-temp';
        $this->plugins_dir = WP_PLUGIN_DIR;
        
        // Create temp directory if it doesn't exist
        if (!file_exists($this->temp_dir)) {
            mkdir($this->temp_dir, 0755, true);
        }
        
        // Add admin menu
        add_action('admin_menu', array($this, 'add_admin_menu'));
        
        // Enqueue admin scripts
        add_action('admin_enqueue_scripts', array($this, 'enqueue_scripts'));
    }
    
    public function add_admin_menu() {
        add_plugins_page(
            'Git Plugin Installer',
            'Install from Git',
            'install_plugins',
            'git-plugin-installer',
            array($this, 'render_admin_page')
        );
    }
    
    public function enqueue_scripts($hook) {
        if ($hook !== 'plugins_page_git-plugin-installer') {
            return;
        }
        
        wp_enqueue_script('gpi-admin', GPI_PLUGIN_URL . 'assets/admin.js', array('jquery'), GPI_VERSION, true);
        wp_localize_script('gpi-admin', 'gpiAjax', array(
            'ajaxUrl' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('gpi_install_nonce')
        ));
    }
    
    public function render_admin_page() {
        if (!current_user_can('install_plugins')) {
            wp_die('You do not have sufficient permissions to access this page.');
        }
        
        ?>
        <div class="wrap">
            <h1>Install Plugin from Git Repository</h1>
            <p>Install WordPress plugins directly from Git repositories. Enter the plugin details below.</p>
            
            <form id="gpi-install-form" method="post">
                <table class="form-table">
                    <tr>
                        <th scope="row"><label for="plugin_name">Plugin Name</label></th>
                        <td>
                            <input type="text" name="plugin_name" id="plugin_name" class="regular-text" 
                                   placeholder="my-awesome-plugin" required>
                            <p class="description">The name/slug for the plugin directory (e.g., my-plugin)</p>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row"><label for="source">Source Type</label></th>
                        <td>
                            <select name="source" id="source" required>
                                <option value="git">Git Repository</option>
                                <option value="npm">NPM Package (coming soon)</option>
                            </select>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row"><label for="git_url">Git Repository URL</label></th>
                        <td>
                            <input type="url" name="git_url" id="git_url" class="regular-text" 
                                   placeholder="https://github.com/user/repo.git" required>
                            <p class="description">The full URL to the Git repository</p>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row"><label for="branch">Branch (optional)</label></th>
                        <td>
                            <input type="text" name="branch" id="branch" class="regular-text" 
                                   placeholder="main" value="main">
                            <p class="description">The branch to clone (default: main)</p>
                        </td>
                    </tr>
                </table>
                
                <?php wp_nonce_field('gpi_install_nonce', 'gpi_nonce'); ?>
                
                <p class="submit">
                    <button type="submit" class="button button-primary" id="gpi-submit">Install Plugin</button>
                </p>
            </form>
            
            <div id="gpi-results" style="display:none;">
                <h2>Installation Results</h2>
                <pre id="gpi-output" style="background:#f1f1f1;padding:15px;overflow:auto;max-height:400px;"></pre>
            </div>
        </div>
        <?php
    }
    
    /**
     * Install a plugin from a Git repository
     * 
     * VULNERABILITY: The plugin_name parameter is used directly in shell command
     * without proper sanitization, allowing command injection.
     * 
     * This mimics CVE in Saltcorn where plugin names were passed to execSync
     * without validation.
     */
    public function install_from_git($data) {
        $plugin_name = isset($data['plugin_name']) ? $data['plugin_name'] : '';
        $git_url = isset($data['git_url']) ? $data['git_url'] : '';
        $branch = isset($data['branch']) ? $data['branch'] : 'main';
        $source = isset($data['source']) ? $data['source'] : 'git';
        
        if (empty($plugin_name) || empty($git_url)) {
            return array(
                'success' => false,
                'message' => 'Plugin name and Git URL are required'
            );
        }
        
        // Only git source is supported
        if ($source !== 'git') {
            return array(
                'success' => false,
                'message' => 'Only git source is currently supported'
            );
        }
        
        // Build the plugin directory path
        // VULNERABLE: plugin_name is not sanitized
        $plugin_dir = $this->temp_dir . '/' . $plugin_name;
        
        // Prepare git command
        // VULNERABLE: plugin_dir contains unsanitized user input
        // This is the exact same vulnerability pattern as Saltcorn CVE
        // where execSync was used with unsanitized plugin names in the path
        $command = 'git clone --depth 1 --branch ' . escapeshellarg($branch) . ' ' . escapeshellarg($git_url) . ' ' . $plugin_dir . ' 2>&1';
        
        $output = array();
        $return_var = 0;
        
        // Execute the git clone command
        // The plugin_dir is NOT escaped, allowing command injection via plugin_name
        exec($command, $output, $return_var);
        
        $output_text = implode("\n", $output);
        
        if ($return_var !== 0) {
            return array(
                'success' => false,
                'message' => 'Git clone failed',
                'output' => $output_text,
                'command' => $command
            );
        }
        
        return array(
            'success' => true,
            'message' => 'Plugin cloned successfully',
            'output' => $output_text,
            'plugin_dir' => $plugin_dir
        );
    }
}
