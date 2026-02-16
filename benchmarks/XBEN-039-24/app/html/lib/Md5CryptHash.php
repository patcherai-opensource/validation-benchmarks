<?php
require_once __DIR__ . '/AbstractHashMethod.php';
require_once __DIR__ . '/HashInterface.php';

/**
 * MD5-based crypt() password hashing implementation.
 * Uses the $1$ prefix for MD5 crypt hashes.
 */
class Md5CryptHash extends AbstractHashMethod implements HashInterface
{
    /**
     * Salt length in bytes for MD5 crypt.
     * @var int
     */
    protected static $saltLength = 6;

    /**
     * Salt suffix character.
     * @var string
     */
    protected static $saltSuffix = '$';

    /**
     * Hash prefix identifying MD5 crypt hashes.
     * @var string
     */
    protected static $hashPrefix = '$1$';

    /**
     * Apply the MD5 crypt settings to a raw salt.
     *
     * @param string $salt Raw salt string
     * @return string Salt with MD5 crypt prefix and suffix
     */
    protected function applySettingsToSalt($salt)
    {
        $saltWithSettings = $salt;
        $requiredLen = $this->getBase64LengthForBytes($this->getSaltLength());
        if (strlen($salt) == $requiredLen) {
            $saltWithSettings = $this->getPrefix() . $salt . $this->getSaltSuffix();
        }
        return $saltWithSettings;
    }

    /**
     * Verify a plaintext password against a stored MD5 crypt hash.
     *
     * @param string $plainPassword Plain-text password
     * @param string $storedHash Stored hash
     * @return bool TRUE if the password matches
     */
    public function verifyPassword($plainPassword, $storedHash)
    {
        $isCorrect = false;
        if ($this->isValidSalt($storedHash)) {
            $isCorrect = password_verify($plainPassword, $storedHash);
        }
        return $isCorrect;
    }

    /**
     * Generate a random salt suitable for this hash method.
     *
     * @return string Random salt string
     */
    protected function generateSalt()
    {
        $randomBytes = random_bytes($this->getSaltLength());
        return $this->base64Encode($randomBytes, $this->getSaltLength());
    }

    /**
     * Create a hashed password using MD5 crypt.
     *
     * @param string $password Plaintext password
     * @param string|null $salt Optional custom salt
     * @return string|null Hashed password or null on failure
     */
    public function createHash($password, $salt = null)
    {
        $hashedPW = null;
        if (!empty($password)) {
            if (empty($salt) || !$this->isValidSalt($salt)) {
                $salt = $this->generateSalt();
            }
            $hashedPW = crypt($password, $this->applySettingsToSalt($salt));
        }
        return $hashedPW;
    }

    /**
     * Check if this hasher can handle the given hash format.
     *
     * @param string $hash The hash to check
     * @return bool TRUE if hash starts with the MD5 crypt prefix
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
     * Check if MD5 crypt is available on this system.
     *
     * @return bool TRUE if available
     */
    public function isAvailable()
    {
        return defined('CRYPT_MD5') && CRYPT_MD5;
    }

    /**
     * Get the salt length for this hashing method.
     *
     * @return int Salt length in bytes
     */
    public function getSaltLength()
    {
        return static::$saltLength;
    }

    /**
     * Get the salt suffix.
     *
     * @return string Salt suffix
     */
    protected function getSaltSuffix()
    {
        return static::$saltSuffix;
    }

    /**
     * Get the hash prefix identifying this method.
     *
     * @return string Hash prefix
     */
    public function getPrefix()
    {
        return static::$hashPrefix;
    }

    /**
     * Check if a hash needs to be regenerated.
     *
     * @param string $hash The hash to check
     * @return bool TRUE if rehash is needed
     */
    public function needsRehash($hash)
    {
        return false;
    }

    /**
     * Validate a salt string for this hashing method.
     *
     * @param string $salt Salt string to validate
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
                    $salt = substr($salt, strlen($this->getPrefix()));
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
}
