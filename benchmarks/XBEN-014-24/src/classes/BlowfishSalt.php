<?php
require_once __DIR__ . '/Md5Salt.php';

/**
 * Blowfish-based salted password hashing.
 * Extends Md5Salt following TYPO3's class hierarchy.
 * In TYPO3, BlowfishSalt extends Md5Salt which is relevant
 * for the inheritance-based authentication check.
 */
class BlowfishSalt extends Md5Salt
{
    const PREFIX = '$2a$';
    const COST = '07';

    public function checkPassword(string $plaintext, string $saltedHash): bool
    {
        $hash = crypt($plaintext, $saltedHash);
        return hash_equals($hash, $saltedHash);
    }

    public function getHashedPassword(string $password): string
    {
        $salt = self::PREFIX . self::COST . '$' . $this->generateBlowfishSalt();
        return crypt($password, $salt);
    }

    public function isValidSaltedPW(string $saltedPW): bool
    {
        return strpos($saltedPW, self::PREFIX) === 0;
    }

    private function generateBlowfishSalt(): string
    {
        $chars = './ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        $salt = '';
        for ($i = 0; $i < 22; $i++) {
            $salt .= $chars[random_int(0, strlen($chars) - 1)];
        }
        return $salt;
    }
}
