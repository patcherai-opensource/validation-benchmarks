<?php

namespace App;

class Router
{
    private array $config;

    public function __construct()
    {
        $this->config = require __DIR__ . '/../config/parameters.php';
    }

    public function dispatch(string $uri, string $method): void
    {
        $uri = parse_url($uri, PHP_URL_PATH);
        $uri = rtrim($uri, '/') ?: '/';

        // Public routes (no auth required)
        if ($uri === '/login' || $uri === '/') {
            if (!$this->isAuthenticated()) {
                $controller = new Controller\SecurityController($this->config);
                if ($method === 'POST' && $uri === '/login') {
                    $controller->loginCheck();
                } else {
                    $controller->loginForm();
                }
                return;
            }
        }

        // Require authentication for all other routes
        if (!$this->isAuthenticated()) {
            header('Location: /login');
            exit;
        }

        // Authenticated routes
        switch (true) {
            case $uri === '/' || $uri === '/dashboard':
                $controller = new Controller\DashboardController($this->config);
                $controller->index();
                break;

            case $uri === '/enrich/products':
                $controller = new Controller\ProductController($this->config);
                $controller->index();
                break;

            case preg_match('#^/enrich/products/(\d+)$#', $uri, $matches) === 1:
                $controller = new Controller\ProductController($this->config);
                $controller->show((int)$matches[1]);
                break;

            case $uri === '/enrich/categories':
                $controller = new Controller\CategoryController($this->config);
                $controller->index();
                break;

            case $uri === '/api/rest/v1/media-files':
                $controller = new Controller\MediaController($this->config);
                if ($method === 'POST') {
                    $controller->postAction();
                } else {
                    $controller->listAction();
                }
                break;

            case $uri === '/collect/channels':
                $controller = new Controller\ChannelController($this->config);
                $controller->index();
                break;

            case $uri === '/settings/locales':
                $controller = new Controller\SettingsController($this->config);
                $controller->locales();
                break;

            case $uri === '/logout':
                $controller = new Controller\SecurityController($this->config);
                $controller->logout();
                break;

            default:
                http_response_code(404);
                echo $this->render404();
                break;
        }
    }

    private function isAuthenticated(): bool
    {
        return isset($_SESSION['user']) && !empty($_SESSION['user']);
    }

    private function render404(): string
    {
        return '<!DOCTYPE html><html><head><title>404 - Akeneo PIM</title></head>'
            . '<body style="font-family: sans-serif; text-align: center; padding: 80px;">'
            . '<h1>404 Not Found</h1><p>The requested page could not be found.</p>'
            . '<a href="/dashboard">Return to Dashboard</a></body></html>';
    }
}