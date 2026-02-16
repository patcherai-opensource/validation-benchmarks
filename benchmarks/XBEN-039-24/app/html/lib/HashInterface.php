<?php
/**
 * Interface for password hashing methods.
 * All hashing implementations must provide these methods.
 */
interface HashInterface
{
    /**
     * Check if a plaintext password matches a stored hash.
     *
     * @param string $plainPassword The plain-text password to verify
     * @param string $storedHash The stored hash to compare against
     * @return bool TRUE if the password matches
     */
    public function verifyPassword($plainPassword, $storedHash);

    /**
     * Create a hashed password string.
     *
     * @param string $password The plaintext password
     * @return string The hashed password
     */
    public function createHash($password);

    /**
     * Check if this hasher can handle the given hash format.
     *
     * @param string $hash The hash to check
     * @return bool TRUE if this hasher recognizes the hash format
     */
    public function canHandleHash($hash);

    /**
     * Check if this hashing method is available on the system.
     *
     * @return bool TRUE if available
     */
    public function isAvailable();

    /**
     * Determine if a stored hash needs to be re-hashed with current settings.
     *
     * @param string $hash The hash to check
     * @return bool TRUE if the hash should be updated
     */
    public function needsRehash($hash);
}
