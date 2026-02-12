<?php
/**
 * Authentication service for SecurePortal.
 * Handles credential verification, 2FA validation, and session management.
 */

function getUsers(): array {
    $usersFile = USERS_FILE;
    if (!file_exists($usersFile)) {
        return [];
    }
    $data = json_decode(file_get_contents($usersFile), true);
    return $data['users'] ?? [];
}

function getUserById(int $id): ?array {
    $users = getUsers();
    foreach ($users as $user) {
        if ($user['id'] === $id) {
            return $user;
        }
    }
    return null;
}

function getUserByUsername(string $username): ?array {
    $users = getUsers();
    foreach ($users as $user) {
        if ($user['username'] === $username) {
            return $user;
        }
    }
    return null;
}

function authenticateCredentials(string $username, string $password): ?array {
    $user = getUserByUsername($username);
    if ($user === null) {
        // Timing-safe comparison to prevent enumeration
        password_verify($password, '$2y$10$dummyhashfortimingnopurpose1234567890abc');
        return null;
    }

    if (!password_verify($password, $user['password_hash'])) {
        return null;
    }

    return $user;
}

function verifyTOTP(array $user, string $code): bool {
    if (!isset($user['totp_secret'])) {
        return false;
    }

    // Simple TOTP verification using the stored secret
    $secret = $user['totp_secret'];
    $timeSlice = floor(time() / TOTP_PERIOD);

    for ($i = -TOTP_WINDOW; $i <= TOTP_WINDOW; $i++) {
        $expectedCode = generateTOTPCode($secret, $timeSlice + $i);
        if (hash_equals($expectedCode, str_pad($code, 6, '0', STR_PAD_LEFT))) {
            return true;
        }
    }

    return false;
}

function generateTOTPCode(string $secret, int $timeSlice): string {
    $secretBytes = base32Decode($secret);
    $time = pack('N*', 0) . pack('N*', $timeSlice);
    $hash = hash_hmac('sha1', $time, $secretBytes, true);
    $offset = ord($hash[19]) & 0x0F;
    $code = (
        ((ord($hash[$offset]) & 0x7F) << 24) |
        ((ord($hash[$offset + 1]) & 0xFF) << 16) |
        ((ord($hash[$offset + 2]) & 0xFF) << 8) |
        (ord($hash[$offset + 3]) & 0xFF)
    ) % 1000000;
    return str_pad((string)$code, 6, '0', STR_PAD_LEFT);
}

function base32Decode(string $input): string {
    $map = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
    $input = strtoupper(rtrim($input, '='));
    $buffer = 0;
    $bitsLeft = 0;
    $result = '';

    for ($i = 0; $i < strlen($input); $i++) {
        $val = strpos($map, $input[$i]);
        if ($val === false) continue;
        $buffer = ($buffer << 5) | $val;
        $bitsLeft += 5;
        if ($bitsLeft >= 8) {
            $bitsLeft -= 8;
            $result .= chr(($buffer >> $bitsLeft) & 0xFF);
        }
    }

    return $result;
}

function isFullyAuthenticated(): bool {
    return isset($_SESSION['auth_stage']) && $_SESSION['auth_stage'] === 'fully_authenticated';
}

function isCredentialsVerified(): bool {
    return isset($_SESSION['auth_stage']) &&
        in_array($_SESSION['auth_stage'], ['credentials_verified', 'fully_authenticated']);
}
