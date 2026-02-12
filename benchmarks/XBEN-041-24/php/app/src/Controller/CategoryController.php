<?php

namespace App\Controller;

class CategoryController
{
    private array $config;

    private array $categories = [
        ['code' => 'master', 'label' => 'Master Catalog', 'parent' => null],
        ['code' => 'monitors', 'label' => 'Monitors', 'parent' => 'master'],
        ['code' => 'accessories', 'label' => 'Accessories', 'parent' => 'master'],
        ['code' => 'cameras', 'label' => 'Cameras', 'parent' => 'master'],
        ['code' => 'networking', 'label' => 'Networking', 'parent' => 'master'],
    ];

    public function __construct(array $config)
    {
        $this->config = $config;
    }

    public function index(): void
    {
        $categories = $this->categories;
        $user = $_SESSION['user'];
        include __DIR__ . '/../../templates/category/index.php';
    }
}