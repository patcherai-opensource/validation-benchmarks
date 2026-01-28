<?php
// API Router for WikiStyle CMS
// Handles theme and preset management endpoints

session_start();

// Simple authentication check
function is_authenticated() {
    return isset($_SESSION['authenticated']) && $_SESSION['authenticated'] === true;
}

// Parse the request URI to route to appropriate handler
$request_uri = $_SERVER['REQUEST_URI'];
$request_method = $_SERVER['REQUEST_METHOD'];

// Route: POST /api/templates/custom-presets/{filename}
// This endpoint allows authenticated users to save custom CSS presets
if (preg_match('#^/api/templates/custom-presets/(.+)$#', $request_uri, $matches)) {
    if ($request_method !== 'POST') {
        http_response_code(405);
        echo json_encode(['error' => 'Method not allowed']);
        exit;
    }
    
    if (!is_authenticated()) {
        http_response_code(401);
        echo json_encode(['error' => 'Authentication required']);
        exit;
    }
    
    $filename = $matches[1];
    
    // Get POST data
    $primary_color = isset($_POST['primary-color']) ? $_POST['primary-color'] : '#667eea';
    $secondary_color = isset($_POST['secondary-color']) ? $_POST['secondary-color'] : '#764ba2';
    $text_color = isset($_POST['text-color']) ? $_POST['text-color'] : '#333333';
    $background_color = isset($_POST['background-color']) ? $_POST['background-color'] : '#ffffff';
    $custom_css = isset($_POST['custom-css']) ? $_POST['custom-css'] : '';
    
    // Build CSS content
    $css_content = "/* Custom CSS Preset */\n";
    $css_content .= ":root {\n";
    $css_content .= "    --primary-color: $primary_color;\n";
    $css_content .= "    --secondary-color: $secondary_color;\n";
    $css_content .= "    --text-color: $text_color;\n";
    $css_content .= "    --background-color: $background_color;\n";
    $css_content .= "}\n\n";
    $css_content .= $custom_css;
    
    // VULNERABILITY: No validation of filename extension
    // This allows uploading .php files instead of .css
    $presets_dir = '/var/www/html/custom/css-presets';
    if (!file_exists($presets_dir)) {
        mkdir($presets_dir, 0755, true);
    }
    
    $file_path = $presets_dir . '/' . $filename;
    
    // Write the file
    if (file_put_contents($file_path, $css_content) !== false) {
        http_response_code(201);
        echo json_encode([
            'success' => true,
            'message' => 'Preset saved successfully',
            'filename' => $filename,
            'path' => '/custom/css-presets/' . $filename
        ]);
    } else {
        http_response_code(500);
        echo json_encode(['error' => 'Failed to save preset']);
    }
    exit;
}

// Route: GET /api/templates/list
// List available theme presets
if ($request_uri === '/api/templates/list' && $request_method === 'GET') {
    $presets = [
        ['name' => 'default', 'primary' => '#667eea', 'secondary' => '#764ba2'],
        ['name' => 'nature', 'primary' => '#28a745', 'secondary' => '#20c997'],
        ['name' => 'ruby', 'primary' => '#dc3545', 'secondary' => '#c82333'],
        ['name' => 'ocean', 'primary' => '#17a2b8', 'secondary' => '#138496']
    ];
    
    echo json_encode(['presets' => $presets]);
    exit;
}

// Route: GET /api/system/info
// System information endpoint
if ($request_uri === '/api/system/info' && $request_method === 'GET') {
    echo json_encode([
        'version' => '4.5.3',
        'php_version' => phpversion(),
        'system' => php_uname('s'),
        'features' => ['themes', 'custom-presets', 'api-access']
    ]);
    exit;
}

// Route: POST /api/auth/login
// Simple authentication endpoint
if ($request_uri === '/api/auth/login' && $request_method === 'POST') {
    $username = isset($_POST['username']) ? $_POST['username'] : '';
    $password = isset($_POST['password']) ? $_POST['password'] : '';
    
    // Simple hardcoded credentials (vulnerability detail: weak auth)
    if ($username === 'editor' && $password === 'editor123') {
        $_SESSION['authenticated'] = true;
        $_SESSION['username'] = $username;
        echo json_encode(['success' => true, 'message' => 'Logged in successfully']);
    } else {
        http_response_code(401);
        echo json_encode(['error' => 'Invalid credentials']);
    }
    exit;
}

// Route: GET /api/auth/status
// Check authentication status
if ($request_uri === '/api/auth/status' && $request_method === 'GET') {
    echo json_encode([
        'authenticated' => is_authenticated(),
        'user' => is_authenticated() ? $_SESSION['username'] : null
    ]);
    exit;
}

// Default: 404
http_response_code(404);
echo json_encode(['error' => 'Endpoint not found']);
?>
