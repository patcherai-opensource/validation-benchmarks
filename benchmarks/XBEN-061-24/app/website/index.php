<?php
error_reporting(0);

require_once 'includes/services/ThemeManager.php';

// Initialize the theme manager for the home page
$themeManager = new ThemeManager();

$metadata = [
    'theme' => 'margot',
    'style' => 'margot.css',
    'squelette' => 'default.html'
];

$themeManager->loadTemplates($metadata);

// Load homepage content
$pageContent = '';
$homeFile = 'pages/HomePage.txt';
if (file_exists($homeFile)) {
    $pageContent = file_get_contents($homeFile);
} else {
    $pageContent = '<h1>Welcome to Encoder64 Wiki</h1><p>A collaborative knowledge base.</p>';
}

$output = $themeManager->render($pageContent, 'Home');
echo $output;
