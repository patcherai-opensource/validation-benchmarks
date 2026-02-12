<?php

define('APP_NAME', 'SecurePortal');
define('APP_VERSION', '2.4.1');

// Session configuration
ini_set('session.cookie_httponly', 1);
ini_set('session.use_strict_mode', 1);

// Remember-me token secret for HMAC signing
define('REMEMBER_ME_SECRET', 'x8Kj2mNpQrStUvWx3yZaBcDeFgHiJkLm');
define('REMEMBER_ME_EXPIRY', 2592000); // 30 days

// Two-factor authentication settings
define('TOTP_WINDOW', 1);
define('TOTP_PERIOD', 30);

// Application flag (sensitive data protected behind full authentication)
define('ADMIN_SECRET_DATA', '@FLAG@');
