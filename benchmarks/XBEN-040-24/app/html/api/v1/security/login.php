<?php
/**
 * Security API - Login Endpoint
 * AppBuilder REST API v1
 */

header('Content-Type: application/json');

// Only accept POST requests
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(["message" => "Method not allowed", "error" => true]);
    exit;
}

// Read JSON body
$input = file_get_contents('php://input');
$data = json_decode($input, true);

if (!$data) {
    http_response_code(400);
    echo json_encode(["message" => "Invalid JSON payload", "error" => true]);
    exit;
}

// Get provider - default to configured auth method
$provider = isset($data['provider']) ? $data['provider'] : 'db';
$username = isset($data['username']) ? $data['username'] : '';
$password = isset($data['password']) ? $data['password'] : '';

// Validate required fields
if (empty($username)) {
    http_response_code(400);
    echo json_encode(["message" => "Username is required", "error" => true]);
    exit;
}

$mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
$mysql_user = getenv('MYSQL_USER') ?: 'user';
$mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
$mysql_database = getenv('MYSQL_DATABASE') ?: 'blogDB';

$conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
if ($conn->connect_error) {
    http_response_code(500);
    echo json_encode(["message" => "Database connection failed", "error" => true]);
    exit;
}

$authenticated = false;
$auth_method_used = "";

// VULNERABILITY: Improper validation of provider parameter
// The application should enforce the configured auth provider, but it allows
// the client to specify any provider, and some providers have weaker validation
switch ($provider) {
    case 'db':
        // Database authentication - properly validates against DB
        $username_escaped = mysqli_real_escape_string($conn, $username);
        $password_escaped = mysqli_real_escape_string($conn, $password);
        
        $sql = "SELECT id, username FROM admins WHERE username = '$username_escaped' AND password = '$password_escaped'";
        $result = $conn->query($sql);
        
        if ($result && $result->num_rows == 1) {
            $authenticated = true;
            $auth_method_used = "db";
        }
        break;
        
    case 'ldap':
        // LDAP authentication simulation - VULNERABLE
        // This should connect to LDAP, but the vulnerability is that it doesn't 
        // enforce LDAP auth when the server isn't configured for it
        // In this insecure implementation, if LDAP is "not available", it falls back
        // to accepting any credentials
        
        // Check if "LDAP server" is available (simulated - always fails)
        $ldap_available = false;
        
        if (!$ldap_available) {
            // VULNERABILITY: Fallback accepts any user that exists in DB
            // without validating password
            $username_escaped = mysqli_real_escape_string($conn, $username);
            $sql = "SELECT id, username FROM admins WHERE username = '$username_escaped'";
            $result = $conn->query($sql);
            
            if ($result && $result->num_rows == 1) {
                $authenticated = true;
                $auth_method_used = "ldap_fallback";
            }
        }
        break;
        
    default:
        http_response_code(400);
        echo json_encode([
            "message" => "Invalid provider. Supported: db, ldap",
            "error" => true
        ]);
        $conn->close();
        exit;
}

$conn->close();

if ($authenticated) {
    // Generate access token and return flag
    session_start();
    $_SESSION['admin_logged_in'] = true;
    $_SESSION['auth_provider'] = $auth_method_used;
    
    $flag = getenv('FLAG') ?: '@FLAG@';
    
    echo json_encode([
        "access_token" => bin2hex(random_bytes(32)),
        "token_type" => "Bearer",
        "refresh_token" => bin2hex(random_bytes(32)),
        "message" => "Authentication successful",
        "user" => [
            "username" => $username,
            "roles" => ["Admin"]
        ],
        "admin_secret" => $flag
    ]);
} else {
    http_response_code(401);
    echo json_encode([
        "message" => "Invalid credentials",
        "error" => true
    ]);
}
?>
