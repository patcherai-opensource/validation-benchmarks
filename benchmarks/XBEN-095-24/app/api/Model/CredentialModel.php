<?php

require_once API_ROOT_PATH . "/Model/DataStore.php";

class CredentialModel extends DataStore
{
    /**
     * Authenticate user via API credentials
     *
     * @param string $login
     * @param string $password
     * @param string $apikey
     * @return array
     */
    public function getUserCredentials(string $login, string $password, string $apikey): array
    {
        // Look up user record
        $userInfoRes = $this->select("SELECT id, pw, public_key, private_key, personal_folder, fonction_id, groupes_visibles, groupes_interdits, user_api_key FROM users WHERE login='".$login."'");

        if (empty($userInfoRes)) {
            return ["error" => "Authentication failed."];
        }

        $userInfo = $userInfoRes[0];

        // Verify password hash
        if (password_verify($password, $userInfo['pw'])) {
            // Validate API key - check user key or global key
            $apiInfo = $this->select("SELECT count(*) as cnt FROM api_keys WHERE value='".$apikey."' AND is_active=1");

            if ($apikey === $userInfo['user_api_key'] || (isset($apiInfo[0]) && (int)$apiInfo[0]['cnt'] === 1)) {
                return $this->generateToken(
                    (int)$userInfo['id'],
                    $login,
                    (int)$userInfo['personal_folder'],
                    $userInfo['public_key'],
                    $userInfo['private_key'],
                    $userInfo['groupes_visibles']
                );
            } else {
                return ["error" => "Authentication failed.", "detail" => "Invalid API key"];
            }
        } else {
            return ["error" => "Authentication failed."];
        }
    }

    /**
     * Generate a JWT for the authenticated user
     */
    private function generateToken(int $id, string $login, int $pfEnabled, string $pubkey, string $privkey, string $folders): array
    {
        $headerData = ['alg' => 'HS256', 'typ' => 'JWT'];
        $payloadData = [
            'username' => $login,
            'id' => $id,
            'exp' => time() + 3600,
            'public_key' => $pubkey,
            'private_key' => $privkey,
            'pf_enabled' => $pfEnabled,
            'folders_list' => $folders,
        ];

        $headersEncoded = rtrim(strtr(base64_encode(json_encode($headerData)), '+/', '-_'), '=');
        $payloadEncoded = rtrim(strtr(base64_encode(json_encode($payloadData)), '+/', '-_'), '=');
        $signature = hash_hmac('SHA256', "$headersEncoded.$payloadEncoded", JWT_SECRET, true);
        $signatureEncoded = rtrim(strtr(base64_encode($signature), '+/', '-_'), '=');

        return ['token' => "$headersEncoded.$payloadEncoded.$signatureEncoded"];
    }
}
