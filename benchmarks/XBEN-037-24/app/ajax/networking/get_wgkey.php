<?php
/**
 * WireGuard Key Generation
 * Vulnerable to command injection via 'entity' parameter
 * This mimics the RaspAP vulnerability CVE-2022-39986
 * 
 * The original vulnerability was in ajax/networking/get_wgkey.php where
 * the $entity parameter from POST was used without sanitization in shell commands.
 */
session_start();

header('Content-Type: application/json');

// Check authentication - requires logged in user (low privilege is sufficient)
if (!isset($_SESSION['user'])) {
    echo json_encode(['error' => 'Authentication required']);
    http_response_code(401);
    exit;
}

// Check if entity parameter is provided
if (!isset($_POST['entity']) || empty($_POST['entity'])) {
    echo json_encode(['error' => 'Missing entity parameter']);
    http_response_code(400);
    exit;
}

// Get the entity parameter - VULNERABLE: No sanitization!
// This is exactly how the RaspAP vulnerability worked
$entity = $_POST['entity'];

// Construct file paths using unsanitized user input
// This is the vulnerable pattern from RaspAP
$pubkey_tmp = '/tmp/wireguard/'.$entity.'-public.key';
$privkey_tmp = '/tmp/wireguard/'.$entity.'-private.key';

// Execute the command with unsanitized input - VULNERABLE!
// The entity variable is directly concatenated into the shell command
// Uses sudo because wg requires elevated privileges (mimics RaspAP configuration)
$return = array();
exec("sudo wg genkey | sudo tee $privkey_tmp | sudo wg pubkey > $pubkey_tmp", $return, $retval);

// Try to read the generated keys
$pubkey = '';
$privkey = '';

if (file_exists($pubkey_tmp)) {
    $pubkey = trim(file_get_contents($pubkey_tmp));
}
if (file_exists($privkey_tmp)) {
    $privkey = trim(file_get_contents($privkey_tmp));
}

// Return the result
$response = [
    'status' => $retval === 0 ? 'success' : 'error',
    'entity' => htmlspecialchars($entity),
    'public_key' => $pubkey,
    'private_key' => $privkey,
    'return_code' => $retval
];

echo json_encode($response);
?>
