<?php

use Twig\Loader\FilesystemLoader;
use Twig\Environment;
use Twig\Extension\SandboxExtension;
use Twig\Sandbox\SecurityPolicy;
use Twig\Sandbox\SecurityNotAllowedFunctionError;
use Twig\Sandbox\SecurityNotAllowedFilterError;
use Twig\Sandbox\SecurityNotAllowedTagError;

require_once __DIR__ . '/vendor/autoload.php';

$username = isset($_POST['username']) ? htmlspecialchars($_POST['username']) : 'Guest';

$loader = new FilesystemLoader(__DIR__ . '/templates');

$tags = ['for', 'if', 'block', 'extends', 'include', 'set', 'do'];
$filters = ['escape', 'raw', 'upper', 'lower', 'striptags', 'replace'];
$methods = [];
$properties = ['name', 'description', 'value'];
$functions = ['range', 'constant', 'cycle', 'include'];

$policy = new SecurityPolicy($tags, $filters, $methods, $properties, $functions);
$sandbox = new SandboxExtension($policy, true);

$twig = new Environment($loader, [
    'debug' => false,
    'charset' => 'UTF-8',
    'auto_reload' => false,
    'strict_variables' => false,
    'autoescape' => 'html',
]);

$twig->addExtension($sandbox);

try {
    echo $twig->render('hello.html.twig', ['username' => $username]);
} catch (\Exception $e) {
    echo 'An error occurred.';
}
