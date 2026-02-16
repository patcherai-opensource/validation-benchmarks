<?php
require_once __DIR__ . '/../../lib/config.php';
require_once __DIR__ . '/../../lib/PackageManager.php';

header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    http_response_code(405);
    echo json_encode(array('error' => 'Method not allowed'));
    exit;
}

$action = isset($_GET['action']) ? $_GET['action'] : 'catalog';

if ($action === 'installed') {
    $manager = new PackageManager(PACKAGES_DIR, INSTALL_DIR);
    echo json_encode(array('installed' => $manager->getInstalledExtensions()));
} else {
    // Built-in extension catalog
    $catalog = array(
        array(
            'id' => 'greeting-extension',
            'name' => 'Greeting Extension',
            'version' => '1.2.0',
            'provider' => 'ExtManager Team',
            'description' => 'Provides greeting functionality for the platform.',
            'requires' => '>=2.0.0'
        ),
        array(
            'id' => 'analytics-extension',
            'name' => 'Analytics Extension',
            'version' => '0.9.1',
            'provider' => 'DataViz Labs',
            'description' => 'Extension for platform analytics and reporting.',
            'requires' => '>=2.0.0'
        ),
        array(
            'id' => 'notification-extension',
            'name' => 'Notification Extension',
            'version' => '1.0.3',
            'provider' => 'AlertCorp',
            'description' => 'Push notification support for the extension framework.',
            'requires' => '>=2.1.0'
        )
    );
    echo json_encode(array('extensions' => $catalog));
}
