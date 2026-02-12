<?php
/**
 * Local configuration for the CMS installation.
 * This mirrors TYPO3's LocalConfiguration.php.
 *
 * The saltedPWHashingMethod defines the default password hashing algorithm.
 * Available options: Md5Salt, BlowfishSalt, PhpassSalt
 *
 * Note: Changing this setting after users have been created with a different
 * hashing method may affect authentication behavior.
 */
return [
    'saltedPWHashingMethod' => 'Md5Salt',
    'siteName' => 'ContentFlow CMS',
    'defaultLanguage' => 'en',
    'sessionTimeout' => 3600,
    'maxLoginAttempts' => 5,
    'lockoutDuration' => 900,
];
