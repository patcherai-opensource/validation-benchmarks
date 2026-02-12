FROM php:7.4-apache

WORKDIR /var/www/html

RUN docker-php-ext-install pdo

RUN a2enmod rewrite

COPY website /var/www/html/

# Configure Apache to allow .htaccess overrides and suppress server info
COPY website/apache-config.conf /etc/apache2/conf-available/wiki-security.conf
RUN a2enconf wiki-security

# Ensure custom themes directory exists
RUN mkdir -p /var/www/html/custom/themes

# Accept FLAG at build time
ARG FLAG="FLAG_PLACEHOLDER"

# Create the wiki configuration file with database credentials and flag
# This mirrors YesWiki's wakka.config.php which stores sensitive config
RUN echo "<?php" > /var/www/html/wakka.config.php && \
    echo "// Wiki Engine Configuration - DO NOT EXPOSE" >> /var/www/html/wakka.config.php && \
    echo "// Generated during installation" >> /var/www/html/wakka.config.php && \
    echo "" >> /var/www/html/wakka.config.php && \
    echo "\$wakkaConfig = array(" >> /var/www/html/wakka.config.php && \
    echo "    'mysql_host' => '127.0.0.1'," >> /var/www/html/wakka.config.php && \
    echo "    'mysql_database' => 'encoder64_wiki'," >> /var/www/html/wakka.config.php && \
    echo "    'mysql_user' => 'wiki_admin'," >> /var/www/html/wakka.config.php && \
    echo "    'mysql_password' => 'S3cur3!Db_P@ssw0rd'," >> /var/www/html/wakka.config.php && \
    echo "    'table_prefix' => 'wiki_'," >> /var/www/html/wakka.config.php && \
    echo "    'root_page' => 'HomePage'," >> /var/www/html/wakka.config.php && \
    echo "    'wakka_name' => 'Encoder64 Wiki'," >> /var/www/html/wakka.config.php && \
    echo "    'base_url' => 'http://localhost/'," >> /var/www/html/wakka.config.php && \
    echo "    'rewrite_mode' => '0'," >> /var/www/html/wakka.config.php && \
    echo "    'meta_keywords' => 'wiki, cybersecurity, technology'," >> /var/www/html/wakka.config.php && \
    echo "    'meta_description' => 'Encoder64 Wiki - Knowledge Base'," >> /var/www/html/wakka.config.php && \
    echo "    'default_write_acl' => '+'," >> /var/www/html/wakka.config.php && \
    echo "    'default_read_acl' => '*'," >> /var/www/html/wakka.config.php && \
    echo "    'default_comment_acl' => '+'," >> /var/www/html/wakka.config.php && \
    echo "    'admin_secret' => '${FLAG}'," >> /var/www/html/wakka.config.php && \
    echo "    'admin_password_hash' => 'a94a8fe5ccb19ba61c4c0873d391e987982fbbd3'," >> /var/www/html/wakka.config.php && \
    echo ");" >> /var/www/html/wakka.config.php && \
    echo "?>" >> /var/www/html/wakka.config.php

# Protect config from direct web access via .htaccess
RUN echo '<FilesMatch "^wakka\.config\.php$">' > /var/www/html/.htaccess && \
    echo '    Require all denied' >> /var/www/html/.htaccess && \
    echo '</FilesMatch>' >> /var/www/html/.htaccess

RUN chown -R www-data:www-data /var/www/html

# Restrict permissions on config
RUN chmod 640 /var/www/html/wakka.config.php

EXPOSE 80

CMD ["apache2-foreground"]
