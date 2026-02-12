<?php

class ImageService {

    private $backend_host;
    private $backend_port = 4455;

    public function __construct() {
        $this->backend_host = getenv('IMAGE_SERVICE_HOST') ?: 'localhost';
    }

    public function callBackend($endpoint, $params = []) {
        $url = "http://{$this->backend_host}:{$this->backend_port}/{$endpoint}";

        $options = [
            'http' => [
                'method' => 'POST',
                'header' => 'Content-Type: application/x-www-form-urlencoded',
                'content' => http_build_query($params),
                'timeout' => 30,
            ]
        ];
        $context = stream_context_create($options);
        $response = @file_get_contents($url, false, $context);

        if ($response === FALSE) {
            return json_encode(['status' => 'error', 'message' => 'Backend service unavailable.']);
        }

        return $response;
    }

    public function uploadImage($data, $ext = 'jpg') {
        return $this->callBackend('sku_process', ['data' => $data, 'ext' => $ext]);
    }

    public function processImage($src, $operation = 'tojpg', $params = []) {
        $params['src'] = $src;
        $params['operation'] = $operation;
        return $this->callBackend('image_operate', $params);
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
$methods = [];
$properties = [];
$functions = ['range', 'constant', 'cycle'];

$policy = new SecurityPolicy($tags, $filters, $methods, $properties, $functions);
$sandbox = new SandboxExtension($policy);

$twig = new Environment($loader);
$twig->addExtension($sandbox);

$image_service = new ImageService();

$action = isset($_POST['action']) ? $_POST['action'] : '';
$result = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    switch ($action) {
        case 'upload':
            $data = isset($_POST['image_data']) ? $_POST['image_data'] : '';
            $ext = isset($_POST['ext']) ? $_POST['ext'] : 'jpg';
            if (!empty($data)) {
                $result = $image_service->uploadImage($data, $ext);
            } else {
                $result = json_encode(['status' => 'error', 'message' => 'No image data provided.']);
            }
            break;

        case 'process':
            $src = isset($_POST['src']) ? $_POST['src'] : '';
            $operation = isset($_POST['operation']) ? $_POST['operation'] : 'tojpg';
            $params = [];
            if (isset($_POST['width'])) $params['width'] = $_POST['width'];
            if (isset($_POST['height'])) $params['height'] = $_POST['height'];
            if (isset($_POST['quality'])) $params['quality'] = $_POST['quality'];
            if (isset($_POST['color'])) $params['color'] = $_POST['color'];

            if (!empty($src)) {
                $result = $image_service->processImage($src, $operation, $params);
            } else {
                $result = json_encode(['status' => 'error', 'message' => 'No source image path provided.']);
            }
            break;

        default:
            $result = json_encode(['status' => 'error', 'message' => 'Unknown action.']);
            break;
    }
}

$client_ip = $_SERVER['REMOTE_ADDR'];

try {
    echo $twig->render('sku_model.html.twig', [
        'result' => $result,
        'client_ip' => $client_ip,
    ]);
} catch (SecurityNotAllowedTagError $e) {
    echo 'Tag not allowed: ' . $e->getTagName();
} catch (SecurityNotAllowedFilterError $e) {
    echo 'Filter not allowed: ' . $e->getFilterName();
} catch (SecurityNotAllowedFunctionError $e) {
    echo 'Function not allowed: ' . $e->getFunctionName();
} catch (\Exception $e) {
    echo 'An error occurred while rendering the page.';
}
