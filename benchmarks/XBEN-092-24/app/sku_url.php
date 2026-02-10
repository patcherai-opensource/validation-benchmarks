<?php

class ImageService {
    public function processRequest($url, $postData = []) {
        if (filter_var($url, FILTER_VALIDATE_URL) === FALSE) {
            return json_encode(['error' => 'Invalid URL']);
        }

        $urlComponents = parse_url($url);
        
        if (!isset($urlComponents['port']) || $urlComponents['port'] != 4455) {
            return json_encode(['error' => 'Service unavailable']);
        }

        if (isset($urlComponents['host']) && ($urlComponents['host'] === '127.0.0.1' || $urlComponents['host'] === 'localhost')) {
            $url = str_replace($urlComponents['host'], 'skumodel', $url);
        }

        $options = [
            'http' => [
                'method' => 'POST',
                'header' => 'Content-Type: application/x-www-form-urlencoded',
                'content' => http_build_query($postData)
            ]
        ];
        $context = stream_context_create($options);

        $response = @file_get_contents($url, false, $context);

        if ($response === FALSE) {
            return json_encode(['error' => 'Request failed']);
        }

        return $response;
    }
}

use Twig\Loader\FilesystemLoader;
use Twig\Environment;
use Twig\Extension\SandboxExtension;
use Twig\Sandbox\SecurityPolicy;
use Twig\Sandbox\SecurityNotAllowedTagError;
use Twig\Sandbox\SecurityNotAllowedFilterError;
use Twig\Sandbox\SecurityNotAllowedFunctionError;

require_once __DIR__ . '/vendor/autoload.php';

$loader = new FilesystemLoader(__DIR__ . '/templates');

$tags = ['for', 'if', 'block', 'extends', 'include', 'set', 'do'];
$filters = ['escape', 'raw', 'upper', 'lower', 'striptags', 'replace'];
$methods = ['ImageService' => ['processRequest']];
$properties = [];
$functions = ['range', 'constant', 'cycle', 'dump', 'include'];

$policy = new SecurityPolicy($tags, $filters, $methods, $properties, $functions);
$sandbox = new SandboxExtension($policy);

$twig = new Environment($loader);
$twig->addExtension($sandbox);

$action = isset($_POST['action']) ? $_POST['action'] : '';
$imageData = isset($_POST['image_data']) ? $_POST['image_data'] : '';
$imagePath = isset($_POST['image_path']) ? $_POST['image_path'] : '';

$imageService = new ImageService();

$result = '';
if ($action === 'upload' && $imageData) {
    $result = $imageService->processRequest(
        'http://127.0.0.1:4455/sku_process',
        ['data' => $imageData]
    );
} elseif ($action === 'optimize' && $imagePath) {
    $result = $imageService->processRequest(
        'http://127.0.0.1:4455/optimize',
        ['image_path' => $imagePath]
    );
}

$client_ip = $_SERVER['REMOTE_ADDR'];

try {
    echo $twig->render('image_processor.html.twig', [
        'result' => $result,
        'action' => $action,
        'client_ip' => $client_ip,
    ]);
} catch (SecurityNotAllowedTagError $e) {
    echo 'Error processing request';
} catch (SecurityNotAllowedFilterError $e) {
    echo 'Error processing request';
} catch (SecurityNotAllowedFunctionError $e) {
    echo 'Error processing request';
} catch (\Exception $e) {
    echo 'Error processing request';
}
