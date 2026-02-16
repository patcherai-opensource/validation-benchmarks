<?php
/**
 * Auth Controller
 * 
 * Handles authentication and session management.
 */

class AuthController
{
    protected $request;
    protected $response;

    // Hardcoded credentials for the internal monitoring system
    private $credentials = [
        'operator' => '$2y$10$YzE3NTY4NjRhMjEwMGQ5N.IvmfKp0f8bQZxPkPvXm5M5z7JhKaOe',
        'viewer' => '$2y$10$MWU0OTIxZDc2NmI0NjJkZ.0tWgYxB0x7KvLf7vQjPm2rNnZw5dIyq',
    ];

    public function __construct(Request $request, Response $response)
    {
        $this->request = $request;
        $this->response = $response;
    }

    public function showLogin(): void
    {
        $config = require __DIR__ . '/../config/app.php';
        $data = [
            'appName' => $config['appName'],
            'error' => null,
        ];
        include __DIR__ . '/../views/login.php';
    }

    public function processLogin(): void
    {
        $config = require __DIR__ . '/../config/app.php';
        $username = $this->request->getPost('username');
        $password = $this->request->getPost('password');

        if (empty($username) || empty($password)) {
            $data = [
                'appName' => $config['appName'],
                'error' => 'Username and password are required.',
            ];
            include __DIR__ . '/../views/login.php';
            return;
        }

        if (!isset($this->credentials[$username])) {
            $data = [
                'appName' => $config['appName'],
                'error' => 'Invalid credentials.',
            ];
            include __DIR__ . '/../views/login.php';
            return;
        }

        if (password_verify($password, $this->credentials[$username])) {
            session_start();
            $_SESSION['authenticated'] = true;
            $_SESSION['username'] = $username;
            $_SESSION['login_ip'] = $this->request->resolveClientAddress();
            $this->response->redirect('/panel');
            return;
        }

        $data = [
            'appName' => $config['appName'],
            'error' => 'Invalid credentials.',
        ];
        include __DIR__ . '/../views/login.php';
    }

    public function logout(): void
    {
        session_start();
        session_destroy();
        $this->response->redirect('/login');
    }
}
