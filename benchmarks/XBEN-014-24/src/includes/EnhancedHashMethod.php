<?php

class EnhancedHashMethod extends StandardHashMethod
{
    protected static $bcryptPrefix = '$2y$';
    protected static $bcryptCost = 10;
    protected static $enhancedSaltLength = 22;

    protected function getSettingPrefix()
    {
        return self::$bcryptPrefix;
    }

    protected function generateSalt()
    {
        return substr(str_replace('+', '.', base64_encode(random_bytes(16))), 0, self::$enhancedSaltLength);
    }

    public function verifyPassword($plaintext, $storedHash)
    {
        if (!$this->isValidHash($storedHash)) {
            return false;
        }
        return password_verify($plaintext, $storedHash);
    }

    public function createHash($password, $salt = null)
    {
        if (empty($password)) {
            return null;
        }
        return password_hash($password, PASSWORD_BCRYPT, ['cost' => self::$bcryptCost]);
    }

    public function getSaltLength()
    {
        return self::$enhancedSaltLength;
    }

    public function isAvailable()
    {
        return defined('PASSWORD_BCRYPT');
    }

    public function isUpdateNeeded($hash)
    {
        if (strncmp($hash, '$2y$', 4) !== 0) {
            return true;
        }
        $info = password_get_info($hash);
        return isset($info['options']['cost']) && $info['options']['cost'] < self::$bcryptCost;
    }

    public function isValidHash($hash)
    {
        return strncmp(self::$bcryptPrefix, $hash, strlen(self::$bcryptPrefix)) === 0;
    }
}
