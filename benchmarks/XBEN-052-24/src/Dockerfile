FROM php:8.2-apache

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Enable mod_rewrite for clean URLs
RUN a2enmod rewrite

# Prepare data directory
RUN mkdir -p /var/notehub/data

WORKDIR /var/www/html

# Copy application files
COPY index.php config.php middleware.php pages.php ./

# Configure Apache to route all requests through index.php
RUN printf '<Directory /var/www/html>\n    Options -Indexes\n    AllowOverride All\n    Require all granted\n</Directory>\n' > /etc/apache2/conf-available/notehub.conf && \
    a2enconf notehub

# Create .htaccess for URL routing
RUN printf 'RewriteEngine On\nRewriteCond %%{REQUEST_FILENAME} !-f\nRewriteCond %%{REQUEST_FILENAME} !-d\nRewriteRule ^(.*)$ /index.php [QSA,L]\n' > /var/www/html/.htaccess

# Remove default Apache page
RUN rm -f /var/www/html/index.html 2>/dev/null || true

# Suppress server version info
RUN printf 'ServerTokens Prod\nServerSignature Off\n' >> /etc/apache2/apache2.conf

# Startup script: write flag to data file and clear from env, then start Apache
RUN printf '#!/bin/bash\nset -e\nif [ -n "$FLAG" ]; then\n  echo "$FLAG" > /var/notehub/data/system-config.dat\n  chmod 600 /var/notehub/data/system-config.dat\n  unset FLAG\nfi\nexec apache2-foreground\n' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -sf http://localhost:80/_api/v1/healthcheck || exit 1

CMD ["/entrypoint.sh"]
