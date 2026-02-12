<?php

namespace App\Controller;

class ChannelController
{
    private array $config;

    private array $channels = [
        ['code' => 'ecommerce', 'label' => 'E-Commerce', 'currencies' => ['USD', 'EUR'], 'locales' => ['en_US', 'fr_FR']],
        ['code' => 'print', 'label' => 'Print Catalog', 'currencies' => ['USD'], 'locales' => ['en_US']],
        ['code' => 'mobile', 'label' => 'Mobile App', 'currencies' => ['USD', 'EUR', 'GBP'], 'locales' => ['en_US', 'fr_FR', 'de_DE']],
    ];

    public function __construct(array $config)
    {
        $this->config = $config;
    }

    public function index(): void
    {
        $channels = $this->channels;
        $user = $_SESSION['user'];
        include __DIR__ . '/../../templates/channel/index.php';
    }
}