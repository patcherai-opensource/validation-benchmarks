<?php
require_once __DIR__ . '/Md5CryptHash.php';

/**
 * Bcrypt (Blowfish) password hashing implementation.
 * Uses the $2y$ prefix for bcrypt hashes.
 *
 * Extends Md5CryptHash as bcrypt is considered an evolution
 * of the crypt()-based hashing methods and shares the same
 * base interface through the crypt() function family.
 */
class BcryptHash extends Md5CryptHash
{
    /**
     * Default cost factor for bcrypt.
     */
    const HASH_COST = 10;

    /**
     * Maximum allowed cost factor.
     */
    const MAX_COST = 17;

    /**
     * Minimum allowed cost factor.
     */
    const MIN_COST = 4;

    /**
     * Current cost factor.
     * @var int
     */
    protected static $cost;

    /**
     * Bcrypt salt length in bytes.
     * @var int
     */
    protected static $bcryptSaltLength = 16;

    /**
     * Bcrypt hash prefix.
     * @var string
     */
    protected static $bcryptPrefix = '$2y$';

    /**
     * Apply bcrypt settings to a salt.
     *
     * @param string $salt Raw salt
     * @return string Salt with bcrypt prefix and cost
     */
    protected function applySettingsToSalt($salt)
    {
        $saltWithSettings = $salt;
        $requiredLen = $this->getBase64LengthForBytes($this->getSaltLength());
        if (strlen($salt) == $requiredLen) {
            $saltWithSettings = $this->getPrefix() . sprintf('%02u', $this->getCost()) . '$' . $salt;
        }
        return $saltWithSettings;
    }

    /**
     * Get the current bcrypt cost factor.
     *
     * @return int Cost factor
     */
    public function getCost()
    {
        return isset(self::$cost) ? self::$cost : self::HASH_COST;
    }

    /**
     * Set the bcrypt cost factor.
     *
     * @param int|null $cost Cost factor to set
     */
    public function setCost($cost = null)
    {
        self::$cost = (!is_null($cost) && is_int($cost) && $cost >= self::MIN_COST && $cost <= self::MAX_COST)
            ? $cost : self::HASH_COST;
    }

    /**
     * Check if bcrypt is available on this system.
     *
     * @return bool TRUE if available
     */
    public function isAvailable()
    {
        return defined('CRYPT_BLOWFISH') && CRYPT_BLOWFISH;
    }

    /**
     * Get the salt length for bcrypt.
     *
     * @return int Salt length in bytes
     */
    public function getSaltLength()
    {
        return self::$bcryptSaltLength;
    }

    /**
     * Get the bcrypt hash prefix.
     *
     * @return string Hash prefix
     */
    public function getPrefix()
    {
        return self::$bcryptPrefix;
    }

    /**
     * Check if a bcrypt hash needs rehashing (e.g., cost changed).
     *
     * @param string $hashedPW Stored hash
     * @return bool TRUE if rehash is needed
     */
    public function needsRehash($hashedPW)
    {
        if (strncmp($hashedPW, '$2', 2) !== 0 || !$this->isValidSalt($hashedPW)) {
            return true;
        }
        $costFromHash = $this->extractCost($hashedPW);
        return (!is_null($costFromHash) && $costFromHash < $this->getCost());
    }

    /**
     * Extract the cost factor from a stored bcrypt hash.
     *
     * @param string $hash Stored hash
     * @return int|null The cost factor or null
     */
    protected function extractCost($hash)
    {
        $costStr = null;
        $setting = substr($hash, strlen($this->getPrefix()));
        $pos = strpos($setting, '$');
        if ($pos !== false && $pos <= 2 && is_numeric(substr($setting, 0, $pos))) {
            $costStr = (int)substr($setting, 0, $pos);
        }
        return $costStr;
    }

    /**
     * Validate a salt for the bcrypt format.
     *
     * @param string $salt Salt to validate
     * @return bool TRUE if valid
     */
    public function isValidSalt($salt)
    {
        $isValid = false;
        $skip = false;
        $requiredLen = $this->getBase64LengthForBytes($this->getSaltLength());
        if (strlen($salt) >= $requiredLen) {
            if (strncmp('$', $salt, 1) === 0) {
                if (strncmp($this->getPrefix(), $salt, strlen($this->getPrefix())) === 0) {
                    $isValid = true;
                    $salt = substr($salt, strrpos($salt, '$') + 1);
                } else {
                    $skip = true;
                }
            }
            if (!$skip && strlen($salt) >= $requiredLen) {
                if (preg_match('/^[' . preg_quote(self::ITOA64, '/') . ']{' . $requiredLen . ',' . $requiredLen . '}$/', substr($salt, 0, $requiredLen))) {
                    $isValid = true;
                }
            }
        }
        return $isValid;
    }

    /**
     * Check if this hasher can handle the given hash format.
     *
     * @param string $hash The hash to check
     * @return bool TRUE if hash is a bcrypt hash
     */
    public function canHandleHash($hash)
    {
        $isValid = (strncmp($this->getPrefix(), $hash, strlen($this->getPrefix())) === 0);
        if ($isValid) {
            $isValid = $this->isValidSalt($hash);
        }
        return $isValid;
    }

    /**
     * Create a bcrypt hash for the given password.
     *
     * @param string $password Plaintext password
     * @param string|null $salt Optional custom salt
     * @return string|null Hashed password
     */
    public function createHash($password, $salt = null)
    {
        $hashedPW = null;
        if (!empty($password)) {
            $hashedPW = password_hash($password, PASSWORD_BCRYPT, [
                'cost' => $this->getCost()
            ]);
        }
        return $hashedPW;
    }
}
