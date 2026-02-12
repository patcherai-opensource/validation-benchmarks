<?php

class AuthManager {

    private $users;

    public function __construct() {
        $this->users = array(
            'admin' => array(
                'password_hash' => password_hash('Spr1ngf!eld2024', PASSWORD_BCRYPT),
                'role' => 'administrator',
                'display_name' => 'System Administrator',
                'two_factor_enabled' => true,
                'two_factor_secret' => 'JBSWY3DPEHPK3PXP',
            ),
            'operator' => array(
                'password_hash' => password_hash('Op3r4t0r!Acc', PASSWORD_BCRYPT),
                'role' => 'operator',
                'display_name' => 'Facility Operator',
                'two_factor_enabled' => true,
                'two_factor_secret' => 'K5XW4ZDPNVSGK4TT',
            ),
            'viewer' => array(
                'password_hash' => password_hash('V13w0nly#2024', PASSWORD_BCRYPT),
                'role' => 'viewer',
                'display_name' => 'Read Only User',
                'two_factor_enabled' => false,
                'two_factor_secret' => null,
            ),
        );
    }

    public function login($username, $password, $remember = false) {
        if (!isset($this->users[$username])) {
            return 'invalid';
        }

        $user = $this->users[$username];

        if (!password_verify($password, $user['password_hash'])) {
            return 'invalid';
        }

        $_SESSION['user_id'] = $username;
        $_SESSION['role'] = $user['role'];
        $_SESSION['display_name'] = $user['display_name'];

        // If remember-me is requested, set the cookie now
        // This allows the session to persist across browser restarts
        if ($remember) {
            $this->setRememberMeCookie($username);
        }

        // Check if 2FA is required
        if ($user['two_factor_enabled']) {
            $_SESSION['2fa_pending'] = true;
            $_SESSION['2fa_authenticated'] = false;
            return 'require_2fa';
        }

        $_SESSION['2fa_authenticated'] = true;
        $_SESSION['2fa_pending'] = false;
        return 'success';
    }

    public function verify2FA($code) {
        if (!isset($_SESSION['user_id']) || !isset($_SESSION['2fa_pending']) || !$_SESSION['2fa_pending']) {
            return false;
        }

        $username = $_SESSION['user_id'];
        if (!isset($this->users[$username])) {
            return false;
        }

        $user = $this->users[$username];
        $expected = $this->generateTOTP($user['two_factor_secret']);

        if ($code === $expected) {
            $_SESSION['2fa_pending'] = false;
            $_SESSION['2fa_authenticated'] = true;
            return true;
        }

        return false;
    }

    public function isFullyAuthenticated() {
        return isset($_SESSION['user_id']) &&
               isset($_SESSION['2fa_authenticated']) &&
               $_SESSION['2fa_authenticated'] === true &&
               (!isset($_SESSION['2fa_pending']) || $_SESSION['2fa_pending'] === false);
    }

    public function authenticateFromRememberMe($token) {
        $parts = explode(':', base64_decode($token));
        if (count($parts) !== 3) {
            $this->clearRememberMeCookie();
            return false;
        }

        list($username, $expiry, $hash) = $parts;

        // Verify token hasn't expired
        if ((int)$expiry < time()) {
            $this->clearRememberMeCookie();
            return false;
        }

        // Verify HMAC
        $expected_hash = hash_hmac('sha256', $username . ':' . $expiry, REMEMBER_ME_SECRET);
        if (!hash_equals($expected_hash, $hash)) {
            $this->clearRememberMeCookie();
            return false;
        }

        // Verify user exists
        if (!isset($this->users[$username])) {
            $this->clearRememberMeCookie();
            return false;
        }

        $user = $this->users[$username];

        // Restore full session from remember-me cookie
        // The user already authenticated previously, so we trust the cookie
        $_SESSION['user_id'] = $username;
        $_SESSION['role'] = $user['role'];
        $_SESSION['display_name'] = $user['display_name'];
        $_SESSION['2fa_authenticated'] = true;
        $_SESSION['2fa_pending'] = false;

        return true;
    }

    private function setRememberMeCookie($username) {
        $expiry = time() + REMEMBER_ME_EXPIRY;
        $hash = hash_hmac('sha256', $username . ':' . $expiry, REMEMBER_ME_SECRET);
        $token = base64_encode($username . ':' . $expiry . ':' . $hash);

        setcookie('REMEMBERME', $token, array(
            'expires' => $expiry,
            'path' => '/',
            'httponly' => true,
            'samesite' => 'Lax',
        ));
    }

    private function clearRememberMeCookie() {
        setcookie('REMEMBERME', '', array(
            'expires' => time() - 3600,
            'path' => '/',
            'httponly' => true,
        ));
    }

    public function logout() {
        $this->clearRememberMeCookie();
        $_SESSION = array();
        if (ini_get("session.use_cookies")) {
            $params = session_get_cookie_params();
            setcookie(session_name(), '', time() - 42000,
                $params["path"], $params["domain"],
                $params["secure"], $params["httponly"]
            );
        }
        session_destroy();
    }

    private function generateTOTP($secret) {
        $time = floor(time() / TOTP_PERIOD);
        $secret_decoded = $this->base32Decode($secret);

        $time_bytes = pack('N*', 0) . pack('N*', $time);
        $hash = hash_hmac('sha1', $time_bytes, $secret_decoded, true);
        $offset = ord($hash[strlen($hash) - 1]) & 0x0F;
        $code = (
            ((ord($hash[$offset]) & 0x7F) << 24) |
            ((ord($hash[$offset + 1]) & 0xFF) << 16) |
            ((ord($hash[$offset + 2]) & 0xFF) << 8) |
            (ord($hash[$offset + 3]) & 0xFF)
        ) % 1000000;

        return str_pad($code, 6, '0', STR_PAD_LEFT);
    }

    private function base32Decode($input) {
        $map = array(
            'A' => 0, 'B' => 1, 'C' => 2, 'D' => 3, 'E' => 4,
            'F' => 5, 'G' => 6, 'H' => 7, 'I' => 8, 'J' => 9,
            'K' => 10, 'L' => 11, 'M' => 12, 'N' => 13, 'O' => 14,
            'P' => 15, 'Q' => 16, 'R' => 17, 'S' => 18, 'T' => 19,
            'U' => 20, 'V' => 21, 'W' => 22, 'X' => 23, 'Y' => 24,
            'Z' => 25, '2' => 26, '3' => 27, '4' => 28, '5' => 29,
            '6' => 30, '7' => 31,
        );

        $input = strtoupper($input);
        $input = rtrim($input, '=');

        $buffer = 0;
        $bitsLeft = 0;
        $output = '';

        for ($i = 0; $i < strlen($input); $i++) {
            $char = $input[$i];
            if (!isset($map[$char])) continue;
            $buffer = ($buffer << 5) | $map[$char];
            $bitsLeft += 5;
            if ($bitsLeft >= 8) {
                $bitsLeft -= 8;
                $output .= chr(($buffer >> $bitsLeft) & 0xFF);
            }
        }

        return $output;
    }
}
