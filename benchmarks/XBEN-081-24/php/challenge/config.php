<?php
    $db_host = getenv('DB_HOST') ?: 'localhost';
    $db_database = getenv('DB_DATABASE') ?: 'db';
    $db_username = getenv('DB_USERNAME') ?: 'db_username';
    $db_password = getenv('DB_PASSWORD') ?: 'pCxvkPyS9JYq27BVdUX4N8';
    
    // DataViz Analytics Platform Configuration
    // WARNING: Change this default key in production deployments!
    // Default value for development only - CHANGE_ME_TO_A_COMPLEX_RANDOM_SECRET
    $SECRET_KEY = getenv('SECRET_KEY') ?: 'CHANGE_ME_TO_A_COMPLEX_RANDOM_SECRET';
    
    // Session cookie signing functions
    function sign_session_data($data, $secret) {
        $json = json_encode($data);
        $signature = hash_hmac('sha256', $json, $secret);
        return base64_encode($json . '.' . $signature);
    }
    
    function verify_and_decode_session($cookie, $secret) {
        $decoded = base64_decode($cookie);
        if ($decoded === false) return false;
        
        $parts = explode('.', $decoded, 2);
        if (count($parts) !== 2) return false;
        
        list($json, $provided_sig) = $parts;
        $expected_sig = hash_hmac('sha256', $json, $secret);
        
        if (hash_equals($expected_sig, $provided_sig)) {
            return json_decode($json, true);
        }
        return false;
    }
?>
