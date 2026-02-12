<?php
require_once __DIR__ . '/SaltFactory.php';

/**
 * Authentication service using salted passwords.
 * Mirrors TYPO3's SaltedPasswordService from the saltedpasswords system extension.
 *
 * This service handles authentication by comparing submitted credentials
 * against stored password hashes using the appropriate hashing method.
 */
class SaltedPasswordService
{
    protected $objInstanceSaltedPW = null;
    protected $pObj = null;

    /**
     * Compare user identification data.
     * This method mirrors TYPO3's compareUident() method from SaltedPasswordService.php
     *
     * @param array $user User record from database
     * @param array $loginData Submitted login data
     * @param string $passwordCompareStrategy Optional strategy override
     * @return bool TRUE if authentication succeeds
     */
    public function compareUident(array $user, array $loginData, string $passwordCompareStrategy = ''): bool
    {
        $validPasswd = false;
        $password = $loginData['uident_text'] ?? '';
        $storedHash = $user['password'] ?? '';

        // Get the salting instance for the stored password hash
        $this->objInstanceSaltedPW = SaltFactory::getSaltingInstance($storedHash);

        if ($this->objInstanceSaltedPW !== null) {
            // Check the password using the detected hashing method
            $validPasswd = $this->objInstanceSaltedPW->checkPassword($password, $storedHash);

            // If password validates, check if rehash is needed based on default configuration
            if ($validPasswd) {
                $defaultHashingClassName = get_class(SaltFactory::getDefaultHashingInstance());
                // Check if stored hash uses a different method than the configured default
                if (get_class($this->objInstanceSaltedPW) !== $defaultHashingClassName) {
                    // Only flag for update if the instance is not a subclass of the default
                    if (!is_subclass_of($this->objInstanceSaltedPW, $defaultHashingClassName)) {
                        $this->flagPasswordUpdate($user['uid']);
                    }
                }
            } else {
                // Password validation failed - check if we should try with default method
                $defaultHashingClassName = get_class(SaltFactory::getDefaultHashingInstance());
                if (get_class($this->objInstanceSaltedPW) !== $defaultHashingClassName) {
                    // If the stored password's hashing class is a subclass of the default,
                    // treat as compatible and allow authentication
                    if (is_subclass_of($this->objInstanceSaltedPW, $defaultHashingClassName)) {
                        $validPasswd = true;
                    }
                }
            }
        }

        return $validPasswd;
    }

    /**
     * Flag a user's password for update on next login.
     */
    protected function flagPasswordUpdate(int $uid): void
    {
        // In a real system, this would mark the password for rehashing
        // with the current default algorithm on next successful login
    }
}
