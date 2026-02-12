<?php

namespace App\Controller;

class SettingsController
{
    private array $config;

    private array $localesList = [
        ['code' => 'en_US', 'label' => 'English (United States)', 'activated' => true],
        ['code' => 'fr_FR', 'label' => 'French (France)', 'activated' => true],
        ['code' => 'de_DE', 'label' => 'German (Germany)', 'activated' => true],
        ['code' => 'es_ES', 'label' => 'Spanish (Spain)', 'activated' => false],
        ['code' => 'ja_JP', 'label' => 'Japanese (Japan)', 'activated' => false],
    ];

    public function __construct(array $config)
    {
        $this->config = $config;
    }

    public function locales(): void
    {
        $locales = $this->localesList;
        $user = $_SESSION['user'];
        include __DIR__ . '/../../templates/settings/locales.php';
    }
}