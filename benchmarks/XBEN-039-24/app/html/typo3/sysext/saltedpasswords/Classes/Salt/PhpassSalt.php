<?php
namespace TYPO3\CMS\Saltedpasswords\Salt;

class PhpassSalt implements SaltInterface
{
    protected static $prefix = '$P$';

    public function checkPassword($plaintext, $saltedHash)
    {
        $hash = $this->getHashedPassword($plaintext, $saltedHash);
        return hash_equals($hash, $saltedHash);
    }

    public function getHashedPassword($password, $salt = null)
    {
        if ($salt === null) {
            $salt = $this->generateSalt();
        }
        return crypt($password, $salt);
    }

    public function isValidSaltedPW($saltedPW)
    {
        return strpos($saltedPW, static::$prefix) === 0;
    }

    protected function generateSalt()
    {
        $bytes = random_bytes(6);
        return static::$prefix . base64_encode($bytes) . '$';
    }
}
