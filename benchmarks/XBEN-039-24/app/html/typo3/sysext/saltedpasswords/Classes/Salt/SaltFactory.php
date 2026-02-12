<?php
namespace TYPO3\CMS\Saltedpasswords\Salt;

require_once __DIR__ . '/SaltInterface.php';
require_once __DIR__ . '/Md5Salt.php';
require_once __DIR__ . '/BlowfishSalt.php';
require_once __DIR__ . '/PhpassSalt.php';

class SaltFactory
{
    protected static $registeredSaltClasses = [
        'TYPO3\\CMS\\Saltedpasswords\\Salt\\Md5Salt' => 'TYPO3\\CMS\\Saltedpasswords\\Salt\\Md5Salt',
        'TYPO3\\CMS\\Saltedpasswords\\Salt\\BlowfishSalt' => 'TYPO3\\CMS\\Saltedpasswords\\Salt\\BlowfishSalt',
        'TYPO3\\CMS\\Saltedpasswords\\Salt\\PhpassSalt' => 'TYPO3\\CMS\\Saltedpasswords\\Salt\\PhpassSalt',
    ];

    public static function getSaltingInstance($saltedHash = '')
    {
        foreach (self::$registeredSaltClasses as $className) {
            $instance = new $className();
            if ($instance->isValidSaltedPW($saltedHash)) {
                return $instance;
            }
        }
        return null;
    }

    public static function getDefaultHashingInstance($mode = 'BE')
    {
        $configuredClass = self::getDefaultHashingClassName($mode);
        if ($configuredClass && class_exists($configuredClass)) {
            return new $configuredClass();
        }
        return new PhpassSalt();
    }

    public static function getDefaultHashingClassName($mode = 'BE')
    {
        $conn = new \mysqli(
            getenv('MYSQL_HOST') ?: '127.0.0.1',
            getenv('MYSQL_USER') ?: 'user',
            getenv('MYSQL_PASSWORD') ?: 'password',
            getenv('MYSQL_DATABASE') ?: 'blogDB'
        );
        if ($conn->connect_error) {
            return 'TYPO3\\CMS\\Saltedpasswords\\Salt\\PhpassSalt';
        }

        $stmt = $conn->prepare("SELECT config_value FROM sys_extension_config WHERE extkey = 'saltedpasswords' AND config_key = ?");
        $configKey = $mode . '.saltedPWHashingMethod';
        $stmt->bind_param('s', $configKey);
        $stmt->execute();
        $result = $stmt->get_result();
        if ($row = $result->fetch_assoc()) {
            $conn->close();
            return $row['config_value'];
        }
        $conn->close();
        return 'TYPO3\\CMS\\Saltedpasswords\\Salt\\PhpassSalt';
    }
}
