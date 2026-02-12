<?php

namespace App\Controller;

class DashboardController
{
    private array $config;

    public function __construct(array $config)
    {
        $this->config = $config;
    }

    public function index(): void
    {
        $user = $_SESSION['user'];
        include __DIR__ . '/../../templates/dashboard/index.php';
    }
}