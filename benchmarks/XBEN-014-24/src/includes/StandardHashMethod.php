<?php

class StandardHashMethod extends AbstractHashMethod
{
    protected static $saltLength = 6;
    protected static $prefix = '$1$';

    protected function getSettingPrefix()
    {
        return self::$prefix;
    }

    protected function generateSalt()
    {
        return substr(str_replace('+', '.', base64_encode(random_bytes(self::$saltLength))), 0, self::$saltLength);
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
        if (empty($salt)) {
            $salt = $this->generateSalt();
        }
        return crypt($password, self::$prefix . $salt . '$');
    }

    public function getSaltLength()
    {
        return self::$saltLength;
    }

    public function isAvailable()
    {
        return true;
    }

    public function isUpdateNeeded($hash)
    {
        return false;
    }

    public function isValidHash($hash)
    {
        return strncmp(self::$prefix, $hash, strlen(self::$prefix)) === 0;
    }
}
