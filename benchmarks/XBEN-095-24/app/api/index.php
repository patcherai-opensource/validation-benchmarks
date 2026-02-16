<?php
header("Content-Type: application/json; charset=UTF-8");
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, POST, OPTIONS");
header("Access-Control-Max-Age: 3600");
header("Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With");

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

require_once __DIR__ . '/inc/bootstrap.php';

$uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$segments = array_values(array_filter(explode('/', $uri)));

$apiIndex = array_search('api', $segments);
if ($apiIndex === false) {
    sendErrorResponse(404, 'Not Found');
}

$route = array_slice($segments, $apiIndex + 1);
$endpoint = isset($route[0]) ? $route[0] : '';
$action = isset($route[1]) ? $route[1] : '';

$settingsResult = checkApiEnabled();
if (!$settingsResult['enabled']) {
    sendErrorResponse(403, 'API access is not enabled');
}

if ($endpoint === 'authenticate') {
    require_once API_ROOT_PATH . '/Controller/CredentialController.php';
    $controller = new CredentialController();
    $controller->verifyAction();

} elseif ($endpoint === 'user' || $endpoint === 'item' || $endpoint === 'folder') {
    $tokenData = validateBearerToken();
    if ($tokenData === null) {
        sendErrorResponse(401, 'Access denied. Invalid or missing token.');
    }

    if ($endpoint === 'user' && $action === 'list') {
        require_once API_ROOT_PATH . '/Controller/MemberController.php';
        $controller = new MemberController();
        $controller->listAction($tokenData);
    } elseif ($endpoint === 'item' && $action === 'inFolders') {
        require_once API_ROOT_PATH . '/Controller/EntryController.php';
        $controller = new EntryController();
        $controller->inFoldersAction($tokenData);
    } elseif ($endpoint === 'folder' && $action === 'list') {
        require_once API_ROOT_PATH . '/Controller/CategoryController.php';
        $controller = new CategoryController();
        $controller->listAction($tokenData);
    } else {
        sendErrorResponse(404, 'Action not found');
    }
} elseif (empty($endpoint)) {
    sendJsonResponse([
        'application' => 'VaultPass API',
        'version' => APP_VERSION,
        'endpoints' => [
            'POST /api/authenticate' => 'Obtain access token',
            'GET /api/user/list' => 'List users (requires token)',
            'GET /api/item/inFolders' => 'List items in folders (requires token)',
            'GET /api/folder/list' => 'List folders (requires token)',
        ]
    ]);
} else {
    sendErrorResponse(404, 'Endpoint not found');
}

function checkApiEnabled() {
    $conn = db_connect();
    if (!$conn) {
        return ['enabled' => false];
    }
    $stmt = $conn->prepare("SELECT setting_value FROM app_settings WHERE setting_key = 'api_enabled'");
    $stmt->execute();
    $result = $stmt->get_result();
    $enabled = false;
    if ($result->num_rows > 0) {
        $row = $result->fetch_assoc();
        $enabled = ($row['setting_value'] === '1');
    }
    $stmt->close();
    $conn->close();
    return ['enabled' => $enabled];
}

function validateBearerToken() {
    $headers = getAuthorizationHeader();
    if (empty($headers)) return null;

    if (preg_match('/Bearer\s(\S+)/', $headers, $matches)) {
        $jwt = $matches[1];
        return verifyJwt($jwt);
    }
    return null;
}

function getAuthorizationHeader() {
    if (isset($_SERVER['Authorization'])) {
        return trim($_SERVER['Authorization']);
    }
    if (isset($_SERVER['HTTP_AUTHORIZATION'])) {
        return trim($_SERVER['HTTP_AUTHORIZATION']);
    }
    if (function_exists('apache_request_headers')) {
        $headers = apache_request_headers();
        $headers = array_combine(array_map('ucwords', array_keys($headers)), array_values($headers));
        if (isset($headers['Authorization'])) {
            return trim($headers['Authorization']);
        }
    }
    return null;
}

function verifyJwt($jwt) {
    $parts = explode('.', $jwt);
    if (count($parts) !== 3) return null;

    $payload = json_decode(base64_decode($parts[1]), true);
    if (!$payload) return null;

    if (isset($payload['exp']) && $payload['exp'] < time()) return null;

    $signature = hash_hmac('SHA256', $parts[0] . '.' . $parts[1], JWT_SECRET, true);
    $expectedSig = rtrim(strtr(base64_encode($signature), '+/', '-_'), '=');

    if ($expectedSig !== $parts[2]) return null;

    return $payload;
}

function sendErrorResponse($code, $message) {
    http_response_code($code);
    echo json_encode(['error' => $message]);
    exit;
}

function sendJsonResponse($data, $code = 200) {
    http_response_code($code);
    echo json_encode($data);
    exit;
}
