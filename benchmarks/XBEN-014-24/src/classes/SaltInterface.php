<?php
/**
 * Interface for salted password hashing methods.
 * Mirrors TYPO3 SaltInterface from saltedpasswords extension.
 */
interface SaltInterface
{
    /**
     * Check if a given plaintext password matches the stored hash
     */
    public function checkPassword(string $plaintext, string $saltedHash): bool;

    /**
     * Generate a salted hash from a plaintext password
     */
    public function getHashedPassword(string $password): string;

    /**
     * Determine if the given hash was created by this method
     */
    public function isValidSaltedPW(string $saltedPW): bool;
}
