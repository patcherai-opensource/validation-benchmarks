<?php
/**
 * Teampass API - Authentication Controller
 * 
 * Handles API authentication requests.
 * Endpoint: POST /api/index.php?action=auth
 */

require_once __DIR__ . '/../../Model/AuthModel.php';

class AuthController {

    private $authModel;

    public function __construct() {
        $this->authModel = new AuthModel();
    }

    /**
     * Process authentication request
     */
    public function authorize() {
        // Read JSON input
        $data = json_decode(file_get_contents("php://input"));

        if (!$data) {
            $this->sendResponse(400, [
                'error' => 'Invalid request body',
                'message' => 'Expected JSON with login, password, and apikey fields'
            ]);
            return;
        }

        $login = isset($data->login) ? $data->login : '';
        $password = isset($data->password) ? $data->password : '';
        $apikey = isset($data->apikey) ? $data->apikey : '';

        if (empty($login) || empty($password)) {
            $this->sendResponse(400, [
                'error' => 'Missing required fields',
                'message' => 'login and password are required'
            ]);
            return;
        }

        // Verify user credentials and API key
        $authResult = $this->authModel->getUserAuth($login, $apikey);

        if ($authResult['error']) {
            $this->sendResponse(401, [
                'error' => 'Authentication failed',
                'message' => $authResult['error']
            ]);
            return;
        }

        if (!$authResult['user']) {
            $this->sendResponse(401, [
                'error' => 'Authentication failed',
                'message' => 'Invalid credentials'
            ]);
            return;
        }

        // Verify password against stored hash
        if (!password_verify($password, $authResult['user']['pw_hash'])) {
            $this->sendResponse(401, [
                'error' => 'Authentication failed',
                'message' => 'Invalid credentials'
            ]);
            return;
        }

        // Check API key validity
        if (!empty($apikey) && !$authResult['api_valid']) {
            $this->sendResponse(401, [
                'error' => 'Authentication failed',
                'message' => 'Invalid API key'
            ]);
            return;
        }

        // Generate session token
        $token = bin2hex(random_bytes(32));

        $this->sendResponse(200, [
            'token' => $token,
            'user' => [
                'id' => $authResult['user']['id'],
                'login' => $authResult['user']['login'],
                'name' => $authResult['user']['name'],
                'lastname' => $authResult['user']['lastname'],
                'admin' => (bool)$authResult['user']['admin']
            ],
            'duration' => API_TOKEN_DURATION
        ]);
    }

    /**
     * Send JSON response
     */
    private function sendResponse($statusCode, $data) {
        http_response_code($statusCode);
        header('Content-Type: application/json');
        echo json_encode($data);
    }
}