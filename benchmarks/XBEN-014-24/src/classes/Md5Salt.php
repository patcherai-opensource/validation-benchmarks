<?php
require_once __DIR__ . '/SaltInterface.php';

/**
 * MD5-based salted password hashing.
 * Implements password hashing using MD5 with salt prefix.
 * Mirrors TYPO3's Md5Salt class.
 */
class Md5Salt implements SaltInterface
{
    const PREFIX = '$1$';

    public function checkPassword(string $plaintext, string $saltedHash): bool
    {
        $hash = crypt($plaintext, $saltedHash);
        return hash_equals($hash, $saltedHash);
    }

    public function getHashedPassword(string $password): string
    {
        $salt = self::PREFIX . $this->generateSalt() . '$';
        return crypt($password, $salt);
    }

    public function isValidSaltedPW(string $saltedPW): bool
    {
        return strpos($saltedPW, self::PREFIX) === 0;
    }

    protected function generateSalt(int $length = 8): string
    {
        $chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789./';
        $salt = '';
        for ($i = 0; $i < $length; $i++) {
            $salt .= $chars[random_int(0, strlen($chars) - 1)];
        }
        return $salt;
    }
}
