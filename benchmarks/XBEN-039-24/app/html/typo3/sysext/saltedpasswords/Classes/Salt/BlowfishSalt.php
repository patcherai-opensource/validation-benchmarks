<?php
namespace TYPO3\CMS\Saltedpasswords\Salt;

require_once __DIR__ . '/Md5Salt.php';

class BlowfishSalt extends Md5Salt
{
    protected static $prefix = '$2a$';

    public function checkPassword($plaintext, $saltedHash)
    {
        return password_verify($plaintext, $saltedHash);
    }

    public function getHashedPassword($password, $salt = null)
    {
        return password_hash($password, PASSWORD_BCRYPT, ['cost' => 8]);
    }

    public function isValidSaltedPW($saltedPW)
    {
        return (strpos($saltedPW, '$2a$') === 0 || strpos($saltedPW, '$2y$') === 0);
    }
}
