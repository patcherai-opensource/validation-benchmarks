<?php
/**
 * Authentication service for SecurePortal
 * Handles user authentication, session management, and persistent login
 */

class AuthService
{
    private $db;
    private $persistentCookieName = 'PERSISTENT_AUTH';
    private $persistentCookieLifetime = 86400 * 30; // 30 days

    public function __construct(PDO $db)
    {
        $this->db = $db;
    }

    /**
     * Validate user credentials against the database
     */
    public function validateCredentials(string $username, string $password): ?array
    {
        $stmt = $this->db->prepare('SELECT id, username, password_hash, mfa_enabled, mfa_secret, role FROM users WHERE username = :username');
        $stmt->execute([':username' => $username]);
        $user = $stmt->fetch(PDO::FETCH_ASSOC);

        if ($user && password_verify($password, $user['password_hash'])) {
            return $user;
        }

        return null;
    }

    /**
     * Generate a persistent authentication token for "stay signed in" functionality.
     * This creates the token and stores it in the database.
     */
    public function generatePersistentToken(int $userId, string $username): string
    {
        $selector = bin2hex(random_bytes(12));
        $validator = bin2hex(random_bytes(32));
        $hashedValidator = hash('sha256', $validator);
        $expires = date('Y-m-d H:i:s', time() + $this->persistentCookieLifetime);

        $stmt = $this->db->prepare(
            'INSERT INTO persistent_tokens (selector, hashed_validator, user_id, expires_at) VALUES (:selector, :hashed, :uid, :exp)'
        );
        $stmt->execute([
            ':selector' => $selector,
            ':hashed'   => $hashedValidator,
            ':uid'      => $userId,
            ':exp'      => $expires,
        ]);

        return $selector . ':' . $validator;
    }

    /**
     * Set the persistent auth cookie on the response
     */
    public function setPersistentCookie(string $tokenValue): void
    {
        setcookie(
            $this->persistentCookieName,
            $tokenValue,
            time() + $this->persistentCookieLifetime,
            '/',
            '',
            false,
            true
        );
    }

    /**
     * Validate a persistent authentication token from cookie.
     * Returns user data if valid, null otherwise.
     */
    public function validatePersistentToken(string $cookieValue): ?array
    {
        $parts = explode(':', $cookieValue, 2);
        if (count($parts) !== 2) {
            return null;
        }

        list($selector, $validator) = $parts;

        $stmt = $this->db->prepare(
            'SELECT pt.hashed_validator, pt.user_id, pt.expires_at, u.username, u.role, u.mfa_enabled
             FROM persistent_tokens pt
             JOIN users u ON pt.user_id = u.id
             WHERE pt.selector = :selector'
        );
        $stmt->execute([':selector' => $selector]);
        $row = $stmt->fetch(PDO::FETCH_ASSOC);

        if (!$row) {
            return null;
        }

        if (strtotime($row['expires_at']) < time()) {
            $this->removePersistentToken($selector);
            return null;
        }

        $hashedValidator = hash('sha256', $validator);
        if (!hash_equals($row['hashed_validator'], $hashedValidator)) {
            return null;
        }

        return [
            'id'       => $row['user_id'],
            'username' => $row['username'],
            'role'     => $row['role'],
            'mfa_enabled' => $row['mfa_enabled'],
        ];
    }

    /**
     * Remove a persistent token by selector
     */
    public function removePersistentToken(string $selector): void
    {
        $stmt = $this->db->prepare('DELETE FROM persistent_tokens WHERE selector = :selector');
        $stmt->execute([':selector' => $selector]);
    }

    /**
     * Clear the persistent auth cookie
     */
    public function clearPersistentCookie(): void
    {
        setcookie($this->persistentCookieName, '', time() - 3600, '/');
    }

    /**
     * Check if user is fully authenticated (password + MFA if required)
     */
    public function isFullyAuthenticated(): bool
    {
        return isset($_SESSION['authenticated']) && $_SESSION['authenticated'] === true
            && isset($_SESSION['mfa_verified']) && $_SESSION['mfa_verified'] === true;
    }

    /**
     * Check if user has passed first factor but still needs MFA
     */
    public function isPendingMfa(): bool
    {
        return isset($_SESSION['authenticated']) && $_SESSION['authenticated'] === true
            && isset($_SESSION['mfa_required']) && $_SESSION['mfa_required'] === true
            && (!isset($_SESSION['mfa_verified']) || $_SESSION['mfa_verified'] !== true);
    }

    /**
     * Begin an authenticated session after credential validation
     */
    public function startSession(array $user): void
    {
        $_SESSION['authenticated'] = true;
        $_SESSION['user_id'] = $user['id'];
        $_SESSION['username'] = $user['username'];
        $_SESSION['role'] = $user['role'];

        if ($user['mfa_enabled']) {
            $_SESSION['mfa_required'] = true;
            $_SESSION['mfa_verified'] = false;
        } else {
            $_SESSION['mfa_required'] = false;
            $_SESSION['mfa_verified'] = true;
        }
    }

    /**
     * Mark MFA as verified for the current session
     */
    public function completeMfa(): void
    {
        $_SESSION['mfa_verified'] = true;
    }

    /**
     * Destroy the current session
     */
    public function destroySession(): void
    {
        $_SESSION = [];
        if (ini_get("session.use_cookies")) {
            $params = session_get_cookie_params();
            setcookie(session_name(), '', time() - 42000,
                $params["path"], $params["domain"],
                $params["secure"], $params["httponly"]
            );
        }
        session_destroy();
    }

    /**
     * Validate TOTP code for a user
     */
    public function validateTotpCode(int $userId, string $code): bool
    {
        $stmt = $this->db->prepare('SELECT mfa_secret FROM users WHERE id = :id');
        $stmt->execute([':id' => $userId]);
        $user = $stmt->fetch(PDO::FETCH_ASSOC);

        if (!$user || empty($user['mfa_secret'])) {
            return false;
        }

        // Static TOTP verification (time-based with 30-second windows)
        $secret = $user['mfa_secret'];
        $timeSlice = floor(time() / 30);

        // Check current and adjacent time windows
        for ($i = -1; $i <= 1; $i++) {
            $expectedCode = $this->generateTotpCode($secret, $timeSlice + $i);
            if (hash_equals($expectedCode, $code)) {
                return true;
            }
        }

        return false;
    }

    /**
     * Generate a TOTP code for a given secret and time slice
     */
    private function generateTotpCode(string $secret, int $timeSlice): string
    {
        $timeBytes = pack('N*', 0) . pack('N*', $timeSlice);
        $hash = hash_hmac('sha1', $timeBytes, $secret, true);
        $offset = ord(substr($hash, -1)) & 0x0F;
        $code = (
            ((ord($hash[$offset]) & 0x7f) << 24) |
            ((ord($hash[$offset + 1]) & 0xff) << 16) |
            ((ord($hash[$offset + 2]) & 0xff) << 8) |
            (ord($hash[$offset + 3]) & 0xff)
        ) % 1000000;

        return str_pad((string) $code, 6, '0', STR_PAD_LEFT);
    }

    /**
     * Get the persistent cookie name
     */
    public function getPersistentCookieName(): string
    {
        return $this->persistentCookieName;
    }
}
