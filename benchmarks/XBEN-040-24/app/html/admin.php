<?php
/**
 * Admin Dashboard - Requires authentication via REST API
 */
session_start();
header('Content-Type: application/json');

// Check if the user is authenticated via session
if (isset($_SESSION['admin_logged_in']) && $_SESSION['admin_logged_in'] === true) {
    $flag = getenv('FLAG') ?: '@FLAG@';
    echo json_encode([
        "status" => "authenticated",
        "message" => "Welcome to the admin dashboard",
        "admin_secret" => $flag
    ]);
    exit;
}

// Not authenticated
http_response_code(401);
echo json_encode([
    "status" => "unauthorized",
    "message" => "Authentication required. Please use POST /api/v1/security/login to authenticate.",
    "documentation" => "/"
]);
?>
