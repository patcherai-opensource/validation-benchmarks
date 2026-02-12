<?php

namespace App\Controller;

class SecurityController
{
    private array $config;

    public function __construct(array $config)
    {
        $this->config = $config;
    }

    public function loginForm(): void
    {
        $error = $_SESSION['login_error'] ?? null;
        unset($_SESSION['login_error']);

        include __DIR__ . '/../../templates/security/login.php';
    }

    public function loginCheck(): void
    {
        $username = $_POST['_username'] ?? '';
        $password = $_POST['_password'] ?? '';

        if (empty($username) || empty($password)) {
            $_SESSION['login_error'] = 'Please enter your credentials.';
            header('Location: /login');
            exit;
        }

        $users = $this->config['users'] ?? [];

        if (!isset($users[$username])) {
            $_SESSION['login_error'] = 'Invalid credentials.';
            header('Location: /login');
            exit;
        }

        $user = $users[$username];
        $passwordHash = hash('sha256', $password);

        if (!hash_equals($user['password_hash'], $passwordHash)) {
            $_SESSION['login_error'] = 'Invalid credentials.';
            header('Location: /login');
            exit;
        }

        $_SESSION['user'] = [
            'username' => $username,
            'first_name' => $user['first_name'],
            'last_name' => $user['last_name'],
            'roles' => $user['roles'],
        ];

        header('Location: /dashboard');
        exit;
    }

    public function logout(): void
    {
        session_destroy();
        header('Location: /login');
        exit;
    }
}