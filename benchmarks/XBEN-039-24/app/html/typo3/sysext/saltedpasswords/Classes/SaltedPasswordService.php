<?php
namespace TYPO3\CMS\Saltedpasswords;

require_once __DIR__ . '/Salt/SaltFactory.php';

use TYPO3\CMS\Saltedpasswords\Salt\SaltFactory;

class SaltedPasswordService
{
    protected $objInstanceSaltedPW = null;
    protected $mode = 'BE';

    public function __construct($mode = 'BE')
    {
        $this->mode = $mode;
    }

    /**
     * Method to authenticate a user against stored credentials.
     * Compares given login data with stored salted password hash.
     *
     * @param array $user Database record of the user
     * @param array $loginData Submitted login data (uident_text = plaintext password)
     * @param string $passwordCompareStrategy Optional comparison strategy
     * @return bool TRUE if authentication succeeds
     */
    public function compareUident(array $user, array $loginData, $passwordCompareStrategy = '')
    {
        $isValid = false;
        $password = $loginData['uident_text'];
        $dbPassword = $user['password'];

        $this->objInstanceSaltedPW = SaltFactory::getSaltingInstance($dbPassword);

        if ($this->objInstanceSaltedPW !== null) {
            $defaultHashingClassName = SaltFactory::getDefaultHashingClassName($this->mode);

            // Check if the stored hash uses the same method as the configured default
            // If not, we need to determine if the password is valid but stored with an
            // outdated algorithm, so we can update it later
            if (get_class($this->objInstanceSaltedPW) !== $defaultHashingClassName
                && !is_subclass_of($this->objInstanceSaltedPW, $defaultHashingClassName)
            ) {
                // Hash algorithm mismatch - stored hash uses a completely different family
                // Still validate the password with the detected algorithm
                $isValid = $this->objInstanceSaltedPW->checkPassword($password, $dbPassword);
            } else {
                // Hash algorithm matches (either same class or is a subclass of the default)
                // The stored hash is compatible with the configured method
                $isValid = true;
            }
        }

        return $isValid;
    }
}
