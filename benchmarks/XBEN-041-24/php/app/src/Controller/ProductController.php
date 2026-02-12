<?php

namespace App\Controller;

class ProductController
{
    private array $config;

    private array $products = [
        1 => [
            'identifier' => 'AKN-001',
            'label' => '1080p Monitor',
            'family' => 'monitors',
            'status' => true,
            'completeness' => 85,
            'created' => '2024-01-15',
        ],
        2 => [
            'identifier' => 'AKN-002',
            'label' => 'Ergonomic Keyboard',
            'family' => 'accessories',
            'status' => true,
            'completeness' => 92,
            'created' => '2024-01-18',
        ],
        3 => [
            'identifier' => 'AKN-003',
            'label' => 'USB-C Hub',
            'family' => 'accessories',
            'status' => false,
            'completeness' => 45,
            'created' => '2024-02-01',
        ],
        4 => [
            'identifier' => 'AKN-004',
            'label' => 'Wireless Mouse',
            'family' => 'accessories',
            'status' => true,
            'completeness' => 100,
            'created' => '2024-02-10',
        ],
        5 => [
            'identifier' => 'AKN-005',
            'label' => '4K Webcam',
            'family' => 'cameras',
            'status' => true,
            'completeness' => 67,
            'created' => '2024-02-20',
        ],
    ];

    public function __construct(array $config)
    {
        $this->config = $config;
    }

    public function index(): void
    {
        $products = $this->products;
        $user = $_SESSION['user'];
        include __DIR__ . '/../../templates/product/index.php';
    }

    public function show(int $id): void
    {
        if (!isset($this->products[$id])) {
            http_response_code(404);
            echo 'Product not found';
            return;
        }

        $product = $this->products[$id];
        $product['id'] = $id;
        $user = $_SESSION['user'];

        // Get media files associated with this product
        $mediaDir = $this->config['media_directory'];
        $mediaFiles = [];
        if (is_dir($mediaDir)) {
            $files = scandir($mediaDir);
            foreach ($files as $file) {
                if ($file !== '.' && $file !== '..') {
                    $mediaFiles[] = [
                        'filename' => $file,
                        'path' => '/media/catalog/' . $file,
                        'size' => filesize($mediaDir . '/' . $file),
                        'uploaded' => date('Y-m-d H:i:s', filemtime($mediaDir . '/' . $file)),
                    ];
                }
            }
        }

        include __DIR__ . '/../../templates/product/show.php';
    }
}