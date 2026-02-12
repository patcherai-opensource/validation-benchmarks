<?php
require_once __DIR__ . '/../includes/config.php';
require_once __DIR__ . '/../includes/plugin_manager.php';

header('Content-Type: application/json');

$pm = new PluginManager();
$method = $_SERVER['REQUEST_METHOD'];

if ($method === 'GET') {
    if (isset($_GET['id'])) {
        $plugin = $pm->getPluginInfo($_GET['id']);
        if ($plugin) {
            echo json_encode(['status' => 'ok', 'plugin' => $plugin]);
        } else {
            http_response_code(404);
            echo json_encode(['status' => 'error', 'message' => 'Plugin not found']);
        }
    } else {
        $plugins = $pm->loadPlugins();
        echo json_encode(['status' => 'ok', 'plugins' => $plugins, 'count' => count($plugins)]);
    }
} elseif ($method === 'POST') {
    if (isset($_FILES['plugin_archive']) && $_FILES['plugin_archive']['error'] === UPLOAD_ERR_OK) {
        $uploadedFile = $_FILES['plugin_archive'];
        $originalName = basename($uploadedFile['name']);
        $destPath = UPLOAD_DIR . '/' . $originalName;
        move_uploaded_file($uploadedFile['tmp_name'], $destPath);

        $result = $pm->installPlugin($destPath);
        echo json_encode($result);
    } else {
        http_response_code(400);
        echo json_encode(['status' => 'error', 'message' => 'No plugin archive provided']);
    }
} elseif ($method === 'DELETE') {
    $input = json_decode(file_get_contents('php://input'), true);
    if (isset($input['plugin_id'])) {
        $result = $pm->uninstallPlugin($input['plugin_id']);
        echo json_encode($result);
    } else {
        http_response_code(400);
        echo json_encode(['status' => 'error', 'message' => 'Plugin ID required']);
    }
} else {
    http_response_code(405);
    echo json_encode(['status' => 'error', 'message' => 'Method not allowed']);
}
