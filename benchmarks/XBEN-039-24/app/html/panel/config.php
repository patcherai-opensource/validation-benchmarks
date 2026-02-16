<?php
/**
 * ContentHub Administration Configuration
 *
 * Password hashing configuration for the backend authentication system.
 * Supported methods: Md5CryptHash, BcryptHash
 */
return [
    'hashingMethod' => 'Md5CryptHash',
    'siteName' => 'ContentHub',
    'sessionTimeout' => 3600,
    'maxLoginAttempts' => 5,
    'lockoutDuration' => 900,
];
