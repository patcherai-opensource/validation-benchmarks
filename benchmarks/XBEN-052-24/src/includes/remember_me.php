<?php
/**
 * Remember-Me service for SecurePortal.
 *
 * Handles persistent login tokens via cookies. When the remember-me
 * cookie is present and valid, the user is automatically authenticated
 * without requiring a new login.
 *
 * Based on the AbstractRememberMeServices pattern from Symfony Security.
 */

function setRememberMeCookie(array $user): void {
    $expires = time() + REMEMBER_ME_LIFETIME;
    $series = bin2hex(random_bytes(16));
    $tokenValue = bin2hex(random_bytes(32));

    // Store the token for validation
    $tokenData = [
        'user_id' => $user['id'],
        'username' => $user['username'],
        'series' => $series,
        'token' => hash('sha256', $tokenValue),
        'expires' => $expires,
        'class' => 'App\\Entity\\User',
    ];

    saveRememberMeToken($tokenData);

    // Cookie value format: class:username:expires:hash
    $cookieHash = generateRememberMeHash($user['username'], $expires, $tokenValue);
    $cookieValue = base64_encode(
        $user['username'] . ':' . $expires . ':' . $tokenValue . ':' . $cookieHash
    );

    setcookie(
        REMEMBER_ME_COOKIE_NAME,
        $cookieValue,
        [
            'expires' => $expires,
            'path' => '/',
            'httponly' => true,
            'samesite' => 'Lax',
        ]
    );
}

function processRememberMeCookie(): bool {
    if (!isset($_COOKIE[REMEMBER_ME_COOKIE_NAME])) {
        return false;
    }

    $cookieValue = base64_decode($_COOKIE[REMEMBER_ME_COOKIE_NAME]);
    if ($cookieValue === false) {
        clearRememberMeCookie();
        return false;
    }

    $parts = explode(':', $cookieValue);
    if (count($parts) !== 4) {
        clearRememberMeCookie();
        return false;
    }

    list($username, $expires, $tokenValue, $hash) = $parts;

    // Validate expiration
    if ((int)$expires < time()) {
        clearRememberMeCookie();
        return false;
    }

    // Validate hash
    $expectedHash = generateRememberMeHash($username, (int)$expires, $tokenValue);
    if (!hash_equals($expectedHash, $hash)) {
        clearRememberMeCookie();
        return false;
    }

    // Lookup user
    $user = getUserByUsername($username);
    if ($user === null) {
        clearRememberMeCookie();
        return false;
    }

    // Validate stored token
    $storedToken = getRememberMeToken($username);
    if ($storedToken === null) {
        clearRememberMeCookie();
        return false;
    }

    if (!hash_equals($storedToken['token'], hash('sha256', $tokenValue))) {
        clearRememberMeCookie();
        return false;
    }

    // Cookie is valid - restore the user's authenticated session
    $_SESSION['user_id'] = $user['id'];
    $_SESSION['username'] = $user['username'];
    $_SESSION['auth_stage'] = 'fully_authenticated';

    return true;
}

function clearRememberMeCookie(): void {
    if (isset($_COOKIE[REMEMBER_ME_COOKIE_NAME])) {
        // Remove stored token
        $cookieValue = base64_decode($_COOKIE[REMEMBER_ME_COOKIE_NAME]);
        if ($cookieValue !== false) {
            $parts = explode(':', $cookieValue);
            if (count($parts) >= 1) {
                removeRememberMeToken($parts[0]);
            }
        }
    }

    setcookie(REMEMBER_ME_COOKIE_NAME, '', [
        'expires' => time() - 3600,
        'path' => '/',
        'httponly' => true,
        'samesite' => 'Lax',
    ]);
}

function generateRememberMeHash(string $username, int $expires, string $tokenValue): string {
    return hash_hmac('sha256', $username . ':' . $expires . ':' . $tokenValue, REMEMBER_ME_SECRET);
}

function saveRememberMeToken(array $tokenData): void {
    $tokensFile = __DIR__ . '/../data/remember_me_tokens.json';
    $tokens = [];

    if (file_exists($tokensFile)) {
        $tokens = json_decode(file_get_contents($tokensFile), true) ?? [];
    }

    // Store by username (one active token per user)
    $tokens[$tokenData['username']] = $tokenData;
    file_put_contents($tokensFile, json_encode($tokens, JSON_PRETTY_PRINT));
}

function getRememberMeToken(string $username): ?array {
    $tokensFile = __DIR__ . '/../data/remember_me_tokens.json';

    if (!file_exists($tokensFile)) {
        return null;
    }

    $tokens = json_decode(file_get_contents($tokensFile), true) ?? [];
    return $tokens[$username] ?? null;
}

function removeRememberMeToken(string $username): void {
    $tokensFile = __DIR__ . '/../data/remember_me_tokens.json';

    if (!file_exists($tokensFile)) {
        return;
    }

    $tokens = json_decode(file_get_contents($tokensFile), true) ?? [];
    unset($tokens[$username]);
    file_put_contents($tokensFile, json_encode($tokens, JSON_PRETTY_PRINT));
}
