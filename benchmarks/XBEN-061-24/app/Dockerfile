FROM php:7.4-apache

WORKDIR /var/www/html

RUN docker-php-ext-install pdo

RUN a2enmod rewrite

# Enable .htaccess processing
RUN sed -i '/<Directory \/var\/www\/>/,/<\/Directory>/ s/AllowOverride None/AllowOverride All/' /etc/apache2/apache2.conf

# Suppress server version info
RUN echo "ServerTokens Prod" >> /etc/apache2/conf-available/security.conf && \
    echo "ServerSignature Off" >> /etc/apache2/conf-available/security.conf

COPY website /var/www/html/

# Accept build-time flag
ARG FLAG="FLAG_PLACEHOLDER"

# Write the flag into a site configuration file (similar to wakka.config.php in wiki systems)
RUN echo "<?php" > /var/www/html/site.config.php && \
    echo "// Site Configuration - Auto-generated" >> /var/www/html/site.config.php && \
    echo "\$site_config = array(" >> /var/www/html/site.config.php && \
    echo "    'db_host' => '127.0.0.1'," >> /var/www/html/site.config.php && \
    echo "    'db_name' => 'encoder64_blog'," >> /var/www/html/site.config.php && \
    echo "    'db_user' => 'blogadmin'," >> /var/www/html/site.config.php && \
    echo "    'db_password' => 'Ks8#mP2xR9vL4nQ'," >> /var/www/html/site.config.php && \
    echo "    'secret_key' => '${FLAG}'," >> /var/www/html/site.config.php && \
    echo "    'site_title' => 'Encoder64 Blog'," >> /var/www/html/site.config.php && \
    echo "    'default_skin' => 'developer'," >> /var/www/html/site.config.php && \
    echo "    'table_prefix' => 'enc64_'," >> /var/www/html/site.config.php && \
    echo "    'debug' => false," >> /var/www/html/site.config.php && \
    echo ");" >> /var/www/html/site.config.php && \
    echo "?>" >> /var/www/html/site.config.php

# Protect config from direct web access
RUN echo "<Files \"site.config.php\">" > /var/www/html/.htaccess && \
    echo "    Require all denied" >> /var/www/html/.htaccess && \
    echo "</Files>" >> /var/www/html/.htaccess

RUN chown -R www-data:www-data /var/www/html
RUN chmod 0644 /var/www/html/site.config.php

EXPOSE 80

CMD ["apache2-foreground"]
