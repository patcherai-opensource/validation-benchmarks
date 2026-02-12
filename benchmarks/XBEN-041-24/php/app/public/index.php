<?php
/**
 * Akeneo PIM Community Edition - Front Controller
 */

session_save_path('/var/www/html/var/sessions');
session_start();

require_once __DIR__ . '/../src/bootstrap.php';

$router = new \App\Router();
$router->dispatch($_SERVER['REQUEST_URI'], $_SERVER['REQUEST_METHOD']);