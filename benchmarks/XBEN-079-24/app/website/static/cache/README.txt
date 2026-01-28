SolarView CDN Cache Directory
==============================

This directory contains cached static assets served through the CDN endpoint.

Configuration: /cdn.php
Cache TTL: 86400 seconds (24 hours)
Base Directory: /var/www/html/static/cache/

Assets are accessed via: /cdn.php?path=<asset_path>

Examples:
- /cdn.php?path=widget-styles.css
- /cdn.php?path=widget-config.json

Note: URL encoding is supported for special characters in paths.
