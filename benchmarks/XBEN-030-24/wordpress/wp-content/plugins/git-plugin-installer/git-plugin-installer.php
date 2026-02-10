<?php
/**
 * Plugin Name: Git Plugin Installer
 * Plugin URI: https://example.com/git-plugin-installer
 * Description: Install WordPress plugins directly from Git repositories. Admin only.
 * Version: 1.0.0
 * Author: CTF Challenge
 * Author URI: https://example.com
 * License: GPL2
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

// Define plugin constants
define('GPI_VERSION', '1.0.0');
define('GPI_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('GPI_PLUGIN_URL', plugin_dir_url(__FILE__));

// Include the main plugin class
require_once GPI_PLUGIN_DIR . 'includes/class-installer.php';

// Initialize the plugin
function gpi_init() {
    new GPI_Installer();
}
add_action('init', 'gpi_init');

// Register AJAX handlers
add_action('wp_ajax_gpi_install_plugin', 'gpi_ajax_install_plugin');

function gpi_ajax_install_plugin() {
    // Verify nonce
    if (!wp_verify_nonce($_POST['nonce'], 'gpi_install_nonce')) {
        wp_send_json_error(array('message' => 'Invalid security token'));
        wp_die();
    }
    
    // Check admin permissions
    if (!current_user_can('install_plugins')) {
        wp_send_json_error(array('message' => 'Insufficient permissions'));
        wp_die();
    }
    
    $installer = new GPI_Installer();
    $result = $installer->install_from_git($_POST);
    
    if ($result['success']) {
        wp_send_json_success($result);
    } else {
        wp_send_json_error($result);
    }
    
    wp_die();
}
