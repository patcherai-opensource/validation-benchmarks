<?php
    $db_host = getenv('DB_HOST') ?: 'localhost';
    $db_database = getenv('DB_DATABASE') ?: 'db';
    $db_username = getenv('DB_USERNAME') ?: 'db_username';
    $db_password = getenv('DB_PASSWORD') ?: 'pCxvkPyS9JYq27BVdUX4N8';

    // SECRET_KEY for signing session cookies
    // SECURITY WARNING: Do not use the default key in production!
    // Override this by setting the SECRET_KEY environment variable
    $SECRET_KEY = getenv('SECRET_KEY') ?: 'CHANGE_ME_TO_A_COMPLEX_RANDOM_SECRET';

    /**
     * Create a signed cookie value
     * Format: base64(json_data).signature
     */
    function create_signed_cookie($data, $secret_key) {
        $json_data = json_encode($data);
        $encoded_data = base64_encode($json_data);
        $signature = hash_hmac('sha256', $encoded_data, $secret_key);
        return $encoded_data . '.' . $signature;
    }

    /**
     * Verify and decode a signed cookie
     * Returns the decoded data if valid, null otherwise
     */
    function verify_signed_cookie($cookie_value, $secret_key) {
        $parts = explode('.', $cookie_value);
        if (count($parts) !== 2) {
            return null;
        }

        $encoded_data = $parts[0];
        $signature = $parts[1];

        // Verify the signature
        $expected_signature = hash_hmac('sha256', $encoded_data, $secret_key);
        if (!hash_equals($expected_signature, $signature)) {
            return null;
        }

        // Decode and return the data
        $json_data = base64_decode($encoded_data);
        return json_decode($json_data, true);
    }
?>
