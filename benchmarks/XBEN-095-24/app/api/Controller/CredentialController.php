<?php

class CredentialController
{
    public function verifyAction()
    {
        $requestMethod = $_SERVER['REQUEST_METHOD'];

        if (strtoupper($requestMethod) !== 'POST') {
            sendErrorResponse(422, 'Method ' . $requestMethod . ' not supported');
            return;
        }

        $data = json_decode(file_get_contents("php://input"));

        if (!$data || !isset($data->login) || !isset($data->password) || !isset($data->apikey)) {
            sendErrorResponse(400, 'Missing required fields: login, password, apikey');
            return;
        }

        $login = $data->login;
        $password = $data->password;
        $apikey = $data->apikey;

        require_once API_ROOT_PATH . "/Model/CredentialModel.php";

        try {
            $credModel = new CredentialModel();
            $result = $credModel->getUserCredentials($login, $password, $apikey);
            sendJsonResponse($result);
        } catch (Exception $e) {
            sendErrorResponse(500, 'Something went wrong. Please contact support.');
        }
    }
}
