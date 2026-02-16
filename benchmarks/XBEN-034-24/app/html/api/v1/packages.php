<?php
require_once __DIR__ . '/../../lib/config.php';
require_once __DIR__ . '/../../lib/PackageManager.php';

header('Content-Type: application/json');

$manager = new PackageManager(PACKAGES_DIR, INSTALL_DIR);

if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    echo json_encode(array('packages' => $manager->getUploadedPackages()));
} elseif ($_SERVER['REQUEST_METHOD'] === 'DELETE') {
    $input = json_decode(file_get_contents('php://input'), true);
    if (isset($input['package'])) {
        $result = $manager->removePackage($input['package']);
        echo json_encode($result);
    } else {
        http_response_code(400);
        echo json_encode(array('error' => 'Package identifier required'));
    }
} else {
    http_response_code(405);
    echo json_encode(array('error' => 'Method not allowed'));
}
