<?php
// JWT utility functions for API authentication

function createJwt($payload, $secret)
{
    $header = base64url_encode(json_encode(['typ' => 'JWT', 'alg' => 'HS256']));
    $payload = base64url_encode(json_encode($payload));
    $signature = base64url_encode(hash_hmac('sha256', "$header.$payload", $secret, true));
    
    return "$header.$payload.$signature";
}

function verifyJwt($token, $secret)
{
    $parts = explode('.', $token);
    if (count($parts) !== 3) {
        return false;
    }
    
    $signature = base64url_encode(hash_hmac('sha256', "{$parts[0]}.{$parts[1]}", $secret, true));
    return hash_equals($signature, $parts[2]);
}

function base64url_encode($data)
{
    return rtrim(strtr(base64_encode($data), '+/', '-_'), '=');
}
