<?php

function create_signed_session($data, $secret_key) {
    $payload = base64_encode(json_encode($data));
    $signature = hash_hmac('sha256', $payload, $secret_key);
    return $payload . '.' . $signature;
}

function verify_and_decode_session($session_cookie, $secret_key) {
    $parts = explode('.', $session_cookie);
    if (count($parts) !== 2) {
        return null;
    }
    
    $payload = $parts[0];
    $signature = $parts[1];
    
    $expected_signature = hash_hmac('sha256', $payload, $secret_key);
    
    if (!hash_equals($expected_signature, $signature)) {
        return null;
    }
    
    $decoded = json_decode(base64_decode($payload), true);
    return $decoded;
}

?>