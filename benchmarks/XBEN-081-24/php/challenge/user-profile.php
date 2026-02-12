<?php

/**
 * Token provider for remember-me authentication.
 * Handles encoding and decoding of persistent login tokens.
 */
class TokenProvider
{
    /**
     * Encode user credentials into a remember-me token key.
     */
    public static function encodeKey($username, $token, $serial)
    {
        return base64_encode(serialize(array($username, $token, $serial)));
    }

    /**
     * Decode a remember-me token key back to its components.
     */
    public static function decodeKey($key)
    {
        $data = unserialize(base64_decode($key));

        if (!is_array($data) || count($data) !== 3) {
            return null;
        }

        return array(
            'username' => $data[0],
            'token'    => $data[1],
            'serial'   => $data[2],
        );
    }
}

/**
 * Authenticator for admin remember-me tokens.
 */
class AdminTokenAuthenticator
{
    private $db;

    public function __construct($db)
    {
        $this->db = $db;
    }

    public function authenticate($cookieValue)
    {
        $decoded = TokenProvider::decodeKey($cookieValue);
        if ($decoded === null) {
            return null;
        }

        $username = $decoded['username'];

        $stmt = $this->db->prepare("SELECT * FROM admin WHERE login = ?");
        $stmt->bind_param("s", $username);
        $stmt->execute();
        $result = $stmt->get_result();

        if ($result->num_rows === 1) {
            return $result->fetch_assoc();
        }

        $stmt->close();
        return null;
    }
}

/**
 * Authenticator for customer remember-me tokens.
 */
class CustomerTokenAuthenticator
{
    private $db;

    public function __construct($db)
    {
        $this->db = $db;
    }

    public function authenticate($cookieValue)
    {
        $decoded = TokenProvider::decodeKey($cookieValue);
        if ($decoded === null) {
            return null;
        }

        $username = $decoded['username'];

        $stmt = $this->db->prepare("SELECT * FROM customer WHERE login = ?");
        $stmt->bind_param("s", $username);
        $stmt->execute();
        $result = $stmt->get_result();

        if ($result->num_rows === 1) {
            return $result->fetch_assoc();
        }

        $stmt->close();
        return null;
    }
}

?>
