<?php
/**
 * Simple template rendering engine
 */

function renderTemplate($name, $data = []) {
    extract($data);
    $templatePath = '/var/www/templates/' . $name . '.php';
    if (file_exists($templatePath)) {
        include $templatePath;
    } else {
        echo 'Template not found: ' . htmlspecialchars($name);
    }
}
