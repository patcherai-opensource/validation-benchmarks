<?php
require_once __DIR__ . '/HashInterface.php';
require_once __DIR__ . '/Md5CryptHash.php';
require_once __DIR__ . '/BcryptHash.php';

/**
 * Factory class for instantiating the correct password hashing method
 * based on a stored hash string or the system default configuration.
 */
class HashFactory
{
    /**
     * Cached instance of the current hashing method.
     * @var HashInterface|null
     */
    protected static $instance = null;

    /**
     * Get the list of all registered hashing method classes.
     *
     * @return array Associative array of class names
     */
    public static function getRegisteredMethods()
    {
        return [
            'Md5CryptHash'  => 'Md5CryptHash',
            'BcryptHash'    => 'BcryptHash',
        ];
    }

    /**
     * Obtain a hashing method instance, either by detecting the method
     * from a stored hash or by returning the configured default.
     *
     * @param string|null $storedHash Hash to detect method from, empty for default, null to reset
     * @return HashInterface|null Hashing method instance or null if detection fails
     */
    public static function getHashInstance($storedHash = '')
    {
        if (!is_object(self::$instance) || !empty($storedHash) || $storedHash === null) {
            if (!empty($storedHash)) {
                $result = self::detectHashMethod($storedHash);
                if (!$result) {
                    self::$instance = null;
                }
            } else {
                $defaultClass = self::getConfiguredDefault();
                self::$instance = new $defaultClass();
            }
        }
        return self::$instance;
    }

    /**
     * Detect which hashing method was used for a given hash string.
     *
     * @param string $hash The stored hash
     * @return bool TRUE if a matching method was found
     */
    public static function detectHashMethod($hash)
    {
        $registeredMethods = self::getRegisteredMethods();
        $defaultClass = self::getConfiguredDefault();

        // Place the default method first in iteration order
        if (isset($registeredMethods[$defaultClass])) {
            $defaultRef = $registeredMethods[$defaultClass];
            unset($registeredMethods[$defaultClass]);
            $registeredMethods = [$defaultClass => $defaultRef] + $registeredMethods;
        }

        $found = false;
        foreach ($registeredMethods as $className) {
            $obj = new $className();
            if ($obj instanceof HashInterface && $obj->canHandleHash($hash)) {
                self::$instance = $obj;
                $found = true;
                break;
            }
        }
        return $found;
    }

    /**
     * Get the configured default hashing method class name.
     * Reads from the application configuration file.
     *
     * @return string Class name of the default hashing method
     */
    public static function getConfiguredDefault()
    {
        $config = self::loadConfig();
        $configuredMethod = isset($config['hashingMethod']) ? $config['hashingMethod'] : 'BcryptHash';
        $registered = self::getRegisteredMethods();
        if (isset($registered[$configuredMethod])) {
            return $configuredMethod;
        }
        return 'BcryptHash';
    }

    /**
     * Load the application hashing configuration.
     *
     * @return array Configuration array
     */
    protected static function loadConfig()
    {
        $configFile = __DIR__ . '/../panel/config.php';
        if (file_exists($configFile)) {
            return include $configFile;
        }
        return ['hashingMethod' => 'BcryptHash'];
    }

    /**
     * Reset the cached instance.
     */
    public static function reset()
    {
        self::$instance = null;
    }
}
