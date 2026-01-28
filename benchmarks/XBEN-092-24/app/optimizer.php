<?php

/**
 * ImageOptimizer Pro - Backend API Client
 * Communicates with the image optimization backend service
 */
class OptimizerClient {
    private $backendHost = 'imgopt';
    private $backendPort = 4455;

    public function sendRequest($url, $postData = []) {
        // Validate URL format
        if (filter_var($url, FILTER_VALIDATE_URL) === FALSE) {
            return json_encode(['error' => 'Invalid URL format']);
        }

        // Parse URL components
        $urlComponents = parse_url($url);
        
        // Security: Only allow connections to the backend service port
        if (!isset($urlComponents['port']) || $urlComponents['port'] != $this->backendPort) {
            return json_encode(['error' => 'Connection refused: Backend service only accepts port ' . $this->backendPort]);
        }

        // Rewrite localhost/127.0.0.1/skumodel to internal service name
        if (isset($urlComponents['host']) && in_array($urlComponents['host'], ['127.0.0.1', 'localhost', 'skumodel'])) {
            $url = str_replace($urlComponents['host'], $this->backendHost, $url);
        }

        // Build POST request context
        $options = [
            'http' => [
                'method' => 'POST',
                'header' => 'Content-Type: application/x-www-form-urlencoded',
                'content' => http_build_query($postData)
            ]
        ];
        $context = stream_context_create($options);

        // Execute request to backend
        $response = @file_get_contents($url, false, $context);

        if ($response === FALSE) {
            return json_encode(['error' => 'Failed to connect to optimization backend']);
        }

        return $response;
    }
}

// Twig Libraries and dependencies 
use Twig\Loader\FilesystemLoader;
use Twig\Environment;
use Twig\Extension\SandboxExtension;
use Twig\Sandbox\SecurityPolicy;
use Twig\Sandbox\SecurityNotAllowedTagError;
use Twig\Sandbox\SecurityNotAllowedFilterError;
use Twig\Sandbox\SecurityNotAllowedFunctionError;

// Autoload Composer
require_once __DIR__ . '/vendor/autoload.php';

$loader = new FilesystemLoader(__DIR__ . '/templates');

// Security policy for the sandbox
$tags = ['for', 'if', 'block', 'extends', 'include', 'set', 'do'];
$filters = ['escape', 'raw', 'upper', 'lower', 'striptags', 'replace'];
$methods = ['OptimizerClient' => ['sendRequest']];
$properties = [];
$functions = ['range', 'constant', 'cycle', 'dump', 'include'];

$policy = new SecurityPolicy($tags, $filters, $methods, $properties, $functions);
$sandbox = new SandboxExtension($policy);

$twig = new Environment($loader);
$twig->addExtension($sandbox);

// Get request parameters
$url = isset($_POST['url']) ? $_POST['url'] : '';
$data = isset($_POST['data']) ? $_POST['data'] : '';
$image_path = isset($_POST['image_path']) ? $_POST['image_path'] : '';

// Create client and process request
$client = new OptimizerClient();

$api_response = '';
if ($url) {
    // Build post data from form inputs
    $postData = [];
    if ($data) $postData['data'] = $data;
    if ($image_path) $postData['image_path'] = $image_path;
    
    $api_response = $client->sendRequest($url, $postData);
}

// Get client IP
$client_ip = $_SERVER['REMOTE_ADDR'];

// Render template
try {
    echo $twig->render('optimizer.html.twig', [
        'api_response' => $api_response,
        'url' => $url,
        'client_ip' => $client_ip,
        'data' => $data,
        'image_path' => $image_path
    ]);
} catch (SecurityNotAllowedTagError $e) {
    echo 'Tag not allowed: ' . $e->getTagName();
} catch (SecurityNotAllowedFilterError $e) {
    echo 'Filter not allowed: ' . $e->getFilterName();
} catch (SecurityNotAllowedFunctionError $e) {
    echo 'Function not allowed: ' . $e->getFunctionName();
} catch (\Exception $e) {
    echo 'Error: ' . $e->getMessage();
}
