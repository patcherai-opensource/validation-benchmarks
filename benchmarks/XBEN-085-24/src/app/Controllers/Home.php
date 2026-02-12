<?php
/**
 * Home Controller
 *
 * Handles the public-facing pages of the application.
 *
 * @package    App\Controllers
 */

class HomeController
{
    protected $request;

    public function __construct($request)
    {
        $this->request = $request;
    }

    /**
     * Display the main dashboard
     */
    public function index(): string
    {
        return $this->renderView('home');
    }

    /**
     * Display the login page
     */
    public function login(): string
    {
        $error = null;

        if ($this->request->getMethod() === 'POST') {
            $username = $this->request->getPost('username');
            $password = $this->request->getPost('password');

            if ($this->authenticate($username, $password)) {
                // Set session
                session_start();
                $_SESSION['authenticated'] = true;
                $_SESSION['username'] = $username;
                $_SESSION['login_time'] = time();
                header('Location: /dashboard');
                exit;
            }

            $error = 'Invalid credentials. Please try again.';
        }

        return $this->renderView('login', ['error' => $error]);
    }

    /**
     * Handle logout
     */
    public function logout(): void
    {
        session_start();
        session_destroy();
        header('Location: /login');
        exit;
    }

    /**
     * Display the user dashboard (requires authentication)
     */
    public function dashboard(): string
    {
        session_start();
        if (empty($_SESSION['authenticated'])) {
            header('Location: /login');
            exit;
        }

        return $this->renderView('dashboard', [
            'username' => $_SESSION['username'] ?? 'User',
            'clientIP' => $this->request->getIPAddress(),
        ]);
    }

    /**
     * API endpoint for system health
     */
    public function health(): void
    {
        header('Content-Type: application/json');
        echo json_encode([
            'status' => 'healthy',
            'timestamp' => date('c'),
            'version' => '4.2.10',
        ]);
    }

    /**
     * About page
     */
    public function about(): string
    {
        return $this->renderView('about');
    }

    /**
     * Authenticate user
     */
    private function authenticate(string $username, string $password): bool
    {
        $users = [
            'operator' => '$2y$10$YJHmCAM8Pq5TmFgMLFpZNOR3.PtX5xr7VRmHqAI4.0DwC0Ckd6fUi',
            'viewer'   => '$2y$10$K2pKgNpJxBn7h9T5dU4oN.f1g3J2kLm8P4qR6sW0vX1yZ2aB3cD4e',
        ];

        if (isset($users[$username])) {
            return password_verify($password, $users[$username]);
        }

        return false;
    }

    /**
     * Render a view template
     */
    private function renderView(string $view, array $data = []): string
    {
        extract($data);
        ob_start();
        $viewPath = __DIR__ . '/../Views/' . $view . '.php';
        if (file_exists($viewPath)) {
            include $viewPath;
        }
        return ob_get_clean();
    }
}
