<?php
/**
 * Dashboard Controller
 * 
 * Handles the public-facing dashboard and status pages.
 */

class DashboardController
{
    protected $request;
    protected $response;

    public function __construct(Request $request, Response $response)
    {
        $this->request = $request;
        $this->response = $response;
    }

    public function index(): void
    {
        $config = require __DIR__ . '/../config/app.php';
        $data = [
            'appName' => $config['appName'],
            'clientIP' => $this->request->resolveClientAddress(),
        ];
        include __DIR__ . '/../views/dashboard.php';
    }

    public function status(): void
    {
        $this->response->json([
            'status' => 'operational',
            'timestamp' => gmdate('Y-m-d\TH:i:s\Z'),
            'framework' => 'NetGuard/4.2.10',
        ]);
    }

    public function health(): void
    {
        $this->response->json([
            'healthy' => true,
        ]);
    }
}
