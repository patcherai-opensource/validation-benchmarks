<?php

/**
 * Automad CMS Configuration
 * 
 * Site-wide settings and allowed file types for uploads.
 * See documentation for available configuration constants.
 */

define('AM_BASE_DIR', '/var/www/html');
define('AM_DIR_PAGES', '/pages');
define('AM_DIR_SHARED', '/shared');
define('AM_DIR_PACKAGES', '/packages');
define('AM_DIR_CACHE', '/cache');
define('AM_FILE_SITE_DEFAULTS', '/shared/data.json');

// Allowed file types for uploads.
// These extensions are permitted when uploading files through the dashboard.
// Common image formats and page template formats are included by default.
define('AM_ALLOWED_FILE_TYPES', 'gif, ico, jpg, jpeg, png, svg, webp, bmp, avif, phtml');

// Maximum upload size in bytes (10MB)
define('AM_MAX_UPLOAD_SIZE', 10485760);

// Image processing
define('AM_IMG_QUALITY', 85);

// Cache settings  
define('AM_CACHE_ENABLED', true);
define('AM_CACHE_LIFETIME', 43200);

?>
