<?php
/**
 * Dolibarr ERP & CRM - Master include file
 *
 * Loads configuration, database connection, and session handling
 *
 * @package  Dolibarr
 */

// Prevent direct access leaks
error_reporting(0);
ini_set('display_errors', '0');

// Load configuration
$conffile = dirname(__DIR__).'/conf/conf.php';
if (!file_exists($conffile)) {
    http_response_code(500);
    die('Configuration error');
}
require_once $conffile;

// Load core classes
require_once __DIR__.'/core/class/database.class.php';
require_once __DIR__.'/core/lib/functions.lib.php';
require_once __DIR__.'/core/class/extrafields.class.php';

// Database connection
$db = new DoliDB(
    $dolibarr_main_db_host,
    $dolibarr_main_db_user,
    $dolibarr_main_db_pass,
    $dolibarr_main_db_name,
    $dolibarr_main_db_port,
    $dolibarr_main_db_prefix
);

if (!$db->connected) {
    http_response_code(503);
    die('Database connection error');
}

// Global configuration object
$conf = new stdClass();
$conf->entity = 1;
$conf->global = new stdClass();
$conf->global->MAIN_LANG_DEFAULT = 'en_US';

// Start session
if (session_status() === PHP_SESSION_NONE) {
    session_name('DOLSESSID_'.md5($dolibarr_main_instance_unique_id));
    session_start();
}

// Load authenticated user if available
$user = null;
if (!empty($_SESSION['dol_login'])) {
    require_once __DIR__.'/user/class/user.class.php';
    $user = new User($db);
    $result = $user->fetch(0, $_SESSION['dol_login']);
    if ($result <= 0) {
        // Invalid session
        unset($_SESSION['dol_login']);
        $user = null;
    }
}

// Global language handler (simplified)
$langs = new stdClass();
$langs->defaultlang = 'en_US';

// Global ExtraFields handler
$extrafields = new ExtraFields($db);
