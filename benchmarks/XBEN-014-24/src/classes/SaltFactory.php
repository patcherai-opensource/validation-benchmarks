<?php
require_once __DIR__ . '/Md5Salt.php';
require_once __DIR__ . '/BlowfishSalt.php';
require_once __DIR__ . '/PhpassSalt.php';

/**
 * Factory class for creating appropriate salt instances based on hash type.
 * Mirrors TYPO3's SaltFactory for the saltedpasswords extension.
 */
class SaltFactory
{
    /**
     * Detect the appropriate salt instance for a given salted hash string.
     */
    public static function getSaltingInstance(string $saltedHash = ''): ?SaltInterface
    {
        $instance = null;
        $blowfish = new BlowfishSalt();
        $md5 = new Md5Salt();
        $phpass = new PhpassSalt();

        if ($blowfish->isValidSaltedPW($saltedHash)) {
            $instance = $blowfish;
        } elseif ($md5->isValidSaltedPW($saltedHash)) {
            $instance = $md5;
        } elseif ($phpass->isValidSaltedPW($saltedHash)) {
            $instance = $phpass;
        }

        return $instance;
    }

    /**
     * Get the default hashing instance from configuration.
     */
    public static function getDefaultHashingInstance(): SaltInterface
    {
        $config = self::loadConfig();
        $className = $config['saltedPWHashingMethod'] ?? 'Md5Salt';

        if (class_exists($className)) {
            return new $className();
        }

        return new Md5Salt();
    }

    private static function loadConfig(): array
    {
        $configFile = __DIR__ . '/../config/localconf.php';
        if (file_exists($configFile)) {
            return include $configFile;
        }
        return [];
    }
}
