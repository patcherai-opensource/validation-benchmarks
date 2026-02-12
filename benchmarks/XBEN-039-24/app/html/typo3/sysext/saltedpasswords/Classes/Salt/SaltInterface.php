<?php
namespace TYPO3\CMS\Saltedpasswords\Salt;

interface SaltInterface
{
    public function checkPassword($plaintext, $saltedHash);
    public function getHashedPassword($password);
    public function isValidSaltedPW($saltedPW);
}
