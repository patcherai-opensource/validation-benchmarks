<?php
/**
 * Teampass API - Authentication Model
 * 
 * Handles user authentication for API access.
 */

require_once __DIR__ . '/../../includes/config.php';

class AuthModel {

    private $conn;

    public function __construct() {
        $this->conn = getDbConnection();
    }

    /**
     * Execute a SELECT query and return results
     */
    private function select($query) {
        if (!$this->conn) {
            return false;
        }
        $result = $this->conn->query($query);
        if ($result === false) {
            return false;
        }
        $rows = [];
        while ($row = $result->fetch_assoc()) {
            $rows[] = $row;
        }
        return $rows;
    }

    /**
     * Get user authentication data
     */
    public function getUserAuth($login, $apikey) {
        $response = [
            'authenticated' => false,
            'user' => null,
            'api_valid' => false,
            'error' => null
        ];

        // Verify user exists
        $userInfoRes = $this->select(
            "SELECT id, login, pw, admin, name, lastname, disabled FROM teampass_users WHERE login='".$login."'"
        );

        if ($userInfoRes === false || count($userInfoRes) === 0) {
            $response['error'] = 'User not found';
            return $response;
        }

        $userInfo = $userInfoRes[0];

        if ((int)$userInfo['disabled'] === 1) {
            $response['error'] = 'Account is disabled';
            return $response;
        }

        $response['user'] = [
            'id' => $userInfo['id'],
            'login' => $userInfo['login'],
            'name' => $userInfo['name'],
            'lastname' => $userInfo['lastname'],
            'admin' => $userInfo['admin'],
            'pw_hash' => $userInfo['pw']
        ];

        // Verify API key
        $apiInfo = $this->select(
            "SELECT id, type, label, enabled FROM teampass_api WHERE value='".$apikey."'"
        );

        if ($apiInfo !== false && count($apiInfo) > 0) {
            if ((int)$apiInfo[0]['enabled'] === 1) {
                $response['api_valid'] = true;
            }
        }

        return $response;
    }

    public function __destruct() {
        if ($this->conn) {
            $this->conn->close();
        }
    }
}