<?php

namespace phpMyFAQ;

class Session
{
    public static function init(): void
    {
        if (session_status() === PHP_SESSION_NONE) {
            session_start();
        }
    }

    public static function isAuthenticated(): bool
    {
        self::init();
        return isset($_SESSION['admin_authenticated']) && $_SESSION['admin_authenticated'] === true;
    }

    public static function login(string $username, string $password): bool
    {
        self::init();

        $configFile = '/var/www/html/config/auth.php';
        if (!file_exists($configFile)) {
            return false;
        }

        $credentials = include $configFile;

        if (isset($credentials[$username]) && password_verify($password, $credentials[$username])) {
            $_SESSION['admin_authenticated'] = true;
            $_SESSION['admin_user'] = $username;
            $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
            return true;
        }

        return false;
    }

    public static function logout(): void
    {
        self::init();
        session_destroy();
    }

    public static function getUser(): ?string
    {
        self::init();
        return $_SESSION['admin_user'] ?? null;
    }

    public static function getCsrfToken(): string
    {
        self::init();
        if (!isset($_SESSION['csrf_token'])) {
            $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
        }
        return $_SESSION['csrf_token'];
    }
}
