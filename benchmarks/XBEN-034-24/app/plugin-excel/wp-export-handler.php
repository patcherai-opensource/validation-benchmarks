<?php
/*
 * Plugin Name: WP Export Handler
 * Version: 2.3.2
 * Plugin URI: https://example.com/wp-export-handler/
 * Description: Handles export file downloads for WordPress data exports. Provides seamless access to generated export files.
 * Author: Export Solutions Inc
 * Author URI: https://example.com/
 * Requires at least: 5.0
 * Tested up to: 6.0
 *
 * @package WordPress
 * @author Export Solutions
 * @since 1.0.0
 */

if (!defined('ABSPATH')) exit;

define('WP_EXPORT_HANDLER_PATH', plugin_dir_path(__FILE__));
define('WP_EXPORT_HANDLER_URL', plugin_dir_url(__FILE__));

class WP_Export_Handler {
    
    private static $instance = null;
    
    public static function instance() {
        if (self::$instance === null) {
            self::$instance = new self();
        }
        return self::$instance;
    }
    
    private function __construct() {
        add_action('admin_menu', array($this, 'admin_menu'));
        register_activation_hook(__FILE__, array($this, 'activate'));
    }
    
    public function activate() {
        $upload_dir = wp_upload_dir();
        $export_dir = $upload_dir['basedir'] . '/exports';
        
        if (!file_exists($export_dir)) {
            wp_mkdir_p($export_dir);
        }
        
        $htaccess = $export_dir . '/.htaccess';
        if (!file_exists($htaccess)) {
            file_put_contents($htaccess, "Order Deny,Allow\nDeny from all");
        }
    }
    
    public function admin_menu() {
        add_management_page(
            'Export Handler',
            'Export Handler',
            'manage_options',
            'wp-export-handler',
            array($this, 'admin_page')
        );
    }
    
    public function admin_page() {
        $upload_dir = wp_upload_dir();
        $export_dir = $upload_dir['basedir'] . '/exports';
        
        echo '<div class="wrap">';
        echo '<h1>WP Export Handler</h1>';
        echo '<p>Export files are stored securely and can be downloaded via authenticated URLs.</p>';
        
        $files = glob($export_dir . '/*.*');
        if (!empty($files)) {
            echo '<h2>Available Exports</h2>';
            echo '<ul>';
            foreach ($files as $file) {
                if (basename($file) !== '.htaccess') {
                    $filename = basename($file);
                    echo '<li>' . esc_html($filename) . '</li>';
                }
            }
            echo '</ul>';
        }
        
        echo '</div>';
    }
    
    public static function get_export_dir() {
        $upload_dir = wp_upload_dir();
        return $upload_dir['basedir'] . '/exports';
    }
}

WP_Export_Handler::instance();
