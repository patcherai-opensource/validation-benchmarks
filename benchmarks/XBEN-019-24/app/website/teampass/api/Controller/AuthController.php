<?php
namespace TeamPass\Api\Controller;

use TeamPass\Api\Model\UserModel;

class AuthController
{
    private $userModel;

    public function __construct()
    {
        $this->userModel = new UserModel();
    }

    public function authenticate($request)
    {
        $login = $request->getParam('login');
        $password = $request->getParam('pw');
        
        if (empty($login) || empty($password)) {
            return $this->jsonResponse(['error' => 'Missing credentials'], 400);
        }

        $user = $this->userModel->findByLogin($login);
        if (!$user || !password_verify($password, $user['pw'])) {
            return $this->jsonResponse(['error' => 'Invalid credentials'], 401);
        }

        $token = $this->generateToken($user);
        return $this->jsonResponse(['token' => $token, 'user_id' => $user['id']]);
    }

    private function generateToken($user)
    {
        return bin2hex(random_bytes(32));
    }

    private function jsonResponse($data, $code = 200)
    {
        http_response_code($code);
        header('Content-Type: application/json');
        echo json_encode($data);
    }
}
