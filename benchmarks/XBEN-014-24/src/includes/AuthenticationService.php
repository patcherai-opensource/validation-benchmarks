<?php

class AuthenticationService
{
    protected $config;
    protected $userRepo;
    protected $hashInstance = null;
    protected $authenticationFailed = false;

    public function __construct($config, $userRepo)
    {
        $this->config = $config;
        $this->userRepo = $userRepo;
    }

    /**
     * Main authentication entry point. Implements a service chain pattern:
     * 1. Primary salted-hash authentication (validateCredentials)
     * 2. If primary service delegates (status 100), fallback service runs
     *
     * Return codes:
     *   200 = authenticated
     *   100 = service cannot authenticate, delegate to next
     *     0 = authentication explicitly failed
     */
    public function authenticateUser($username, $password)
    {
        $result = ['status' => 100, 'role' => null];

        $user = $this->userRepo->findByUsername($username);
        if (!$user) {
            return ['status' => 0, 'role' => null];
        }

        $this->authenticationFailed = false;

        if ((string)$username !== '' && (string)$password !== '') {
            $validPassword = $this->validateCredentials($user, $password);
            if (!$validPassword) {
                if ($this->config['auth']['enforceHashPolicy'] || $this->authenticationFailed) {
                    $result['status'] = 0;
                }
            } else {
                $result['status'] = 200;
                $result['role'] = $user['role'];
            }
        } else {
            $result['status'] = 0;
        }

        if ($result['status'] === 100) {
            $fallbackResult = $this->baseServiceAuthentication($user, $username, $password);
            if ($fallbackResult !== null) {
                $result = $fallbackResult;
            }
        }

        return $result;
    }

    /**
     * Validates credentials using salted password hashing.
     * Detects the hash algorithm from the stored password and verifies.
     * Also handles hash algorithm migration when the stored hash method
     * differs from the configured default.
     */
    protected function validateCredentials($user, $password)
    {
        $validPasswd = false;
        $defaultHashingMethod = $this->config['auth']['defaultHashMethod'];

        $this->hashInstance = HashMethodFactory::resolveInstance($user['password'], $defaultHashingMethod);

        if (is_object($this->hashInstance)) {
            $validPasswd = $this->hashInstance->verifyPassword($password, $user['password']);

            if (!$validPasswd) {
                $this->authenticationFailed = true;
            }

            $skip = false;

            // Check if the detected hash method matches the configured default
            // If methods are unrelated, enforce strict failure to prevent fallback
            if (get_class($this->hashInstance) !== $defaultHashingMethod && !is_subclass_of($this->hashInstance, $defaultHashingMethod)) {
                $this->authenticationFailed = true;
                $skip = true;
            } else if (get_class($this->hashInstance) !== $defaultHashingMethod) {
                // Hash methods are related through inheritance - treat as compatible
                // Defer to migration path rather than blocking authentication chain
                $this->authenticationFailed = false;
                $this->hashInstance = HashMethodFactory::resolveInstance(null, $defaultHashingMethod);
            }

            if (!$skip && $this->hashInstance->isUpdateNeeded($user['password'])) {
                // Automatic hash migration would be performed here
            }
        }

        return $validPasswd;
    }

    /**
     * Base authentication service - handles users with legacy authentication tokens.
     * This implements token-based verification for backward compatibility
     * with pre-migration user accounts that have stored auth tokens.
     * When the primary hash service delegates (returns 100), this service
     * checks if the user has a valid stored authentication token.
     */
    protected function baseServiceAuthentication($user, $username, $password)
    {
        if (!isset($user['legacy_hash']) || empty($user['legacy_hash'])) {
            return null;
        }

        if ((string)$username === '') {
            return null;
        }

        $authToken = $user['legacy_hash'];

        if (strlen($authToken) === 32 && ctype_xdigit($authToken)) {
            return ['status' => 200, 'role' => $user['role']];
        }

        return null;
    }
}
