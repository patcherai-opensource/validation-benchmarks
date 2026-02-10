<?php
session_start();

header('Content-Type: application/json');

function is_logged_in() {
    return isset($_SESSION['user_id']) && isset($_SESSION['username']);
}

function send_json($data, $status = 200) {
    http_response_code($status);
    echo json_encode($data);
    exit;
}

function send_error($message, $status = 400) {
    send_json(['success' => false, 'error' => $message], $status);
}

$request_uri = $_SERVER['REQUEST_URI'];
$path = parse_url($request_uri, PHP_URL_PATH);
$path = preg_replace('#^/api/#', '', $path);
$method = $_SERVER['REQUEST_METHOD'];

if (preg_match('#^templates/custom-presets/(.+)$#', $path, $matches)) {
    $preset_filename = urldecode($matches[1]);
    
    if ($method === 'POST') {
        if (!is_logged_in()) {
            send_error('Authentication required', 401);
        }
        
        $presets_dir = __DIR__ . '/custom/css-presets';
        
        if (!is_dir($presets_dir)) {
            mkdir($presets_dir, 0755, true);
        }
        
        $primary_color = isset($_POST['primary-color']) ? $_POST['primary-color'] : '#3498db';
        $secondary_color = isset($_POST['secondary-color']) ? $_POST['secondary-color'] : '#2ecc71';
        $background_color = isset($_POST['background-color']) ? $_POST['background-color'] : '#ffffff';
        $text_color = isset($_POST['text-color']) ? $_POST['text-color'] : '#333333';
        $font_family = isset($_POST['font-family']) ? $_POST['font-family'] : 'Arial, sans-serif';
        
        $css_content = ":root {\n";
        $css_content .= "    --primary-color: " . $primary_color . ";\n";
        $css_content .= "    --secondary-color: " . $secondary_color . ";\n";
        $css_content .= "    --background-color: " . $background_color . ";\n";
        $css_content .= "    --text-color: " . $text_color . ";\n";
        $css_content .= "    --font-family: " . $font_family . ";\n";
        $css_content .= "}\n\n";
        $css_content .= "body {\n";
        $css_content .= "    background-color: var(--background-color);\n";
        $css_content .= "    color: var(--text-color);\n";
        $css_content .= "    font-family: var(--font-family);\n";
        $css_content .= "}\n\n";
        $css_content .= ".btn-primary {\n";
        $css_content .= "    background-color: var(--primary-color);\n";
        $css_content .= "}\n\n";
        $css_content .= ".btn-secondary {\n";
        $css_content .= "    background-color: var(--secondary-color);\n";
        $css_content .= "}\n";
        
        $filepath = $presets_dir . DIRECTORY_SEPARATOR . $preset_filename;
        
        if (file_put_contents($filepath, $css_content) !== false) {
            send_json([
                'success' => true,
                'message' => 'Preset created successfully',
                'filename' => $preset_filename,
                'path' => '/custom/css-presets/' . $preset_filename
            ]);
        } else {
            send_error('Failed to save preset', 500);
        }
    } elseif ($method === 'DELETE') {
        if (!is_logged_in()) {
            send_error('Authentication required', 401);
        }
        
        $presets_dir = __DIR__ . '/custom/css-presets';
        $filepath = $presets_dir . DIRECTORY_SEPARATOR . $preset_filename;
        
        if (file_exists($filepath) && unlink($filepath)) {
            send_json(['success' => true, 'message' => 'Preset deleted']);
        } else {
            send_error('Failed to delete preset', 500);
        }
    } else {
        send_error('Method not allowed', 405);
    }
} elseif ($path === 'templates/custom-presets') {
    if ($method === 'GET') {
        $presets_dir = __DIR__ . '/custom/css-presets';
        $presets = [];
        
        if (is_dir($presets_dir)) {
            $files = scandir($presets_dir);
            foreach ($files as $file) {
                if ($file !== '.' && $file !== '..' && !is_dir($presets_dir . '/' . $file)) {
                    $presets[] = $file;
                }
            }
        }
        
        send_json(['success' => true, 'presets' => $presets]);
    } else {
        send_error('Method not allowed', 405);
    }
} elseif ($path === 'user/profile') {
    if (!is_logged_in()) {
        send_error('Authentication required', 401);
    }
    
    if ($method === 'GET') {
        send_json([
            'success' => true,
            'user' => [
                'id' => $_SESSION['user_id'],
                'username' => $_SESSION['username'],
                'role' => $_SESSION['role'] ?? 'user'
            ]
        ]);
    } else {
        send_error('Method not allowed', 405);
    }
} else {
    send_error('Endpoint not found', 404);
}
