<?php
require_once __DIR__ . '/SaltInterface.php';

/**
 * Portable PHP password hashing (PHPass).
 * This is the default hashing method in standard TYPO3 installations.
 * Does NOT extend Md5Salt, so the inheritance bypass does not apply.
 */
class PhpassSalt implements SaltInterface
{
    const PREFIX = '$P$';

    public function checkPassword(string $plaintext, string $saltedHash): bool
    {
        $hash = crypt($plaintext, $saltedHash);
        return hash_equals($hash, $saltedHash);
    }

    public function getHashedPassword(string $password): string
    {
        return password_hash($password, PASSWORD_BCRYPT);
    }

    public function isValidSaltedPW(string $saltedPW): bool
    {
        return strpos($saltedPW, self::PREFIX) === 0;
    }
}
