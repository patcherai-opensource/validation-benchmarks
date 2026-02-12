FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    sed \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY ./website/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt && rm /tmp/requirements.txt

# Set up TeamPass directory structure
RUN mkdir -p /var/www/teampass/webapp/app/templates

# Copy TeamPass static directories first (these simulate the real TeamPass file layout)
COPY ./website/teampass/ /var/www/teampass/

# Copy static assets (CSS/JS) into the teampass web root
COPY ./website/app/static/css/ /var/www/teampass/css/
COPY ./website/app/static/js/ /var/www/teampass/js/

# Copy Flask application (handles dynamic routes: login, dashboard, API)
COPY ./website/app/__init__.py /var/www/teampass/webapp/app/__init__.py
COPY ./website/app/routes.py /var/www/teampass/webapp/app/routes.py
COPY ./website/app/templates/ /var/www/teampass/webapp/app/templates/
COPY ./website/run.py /var/www/teampass/webapp/run.py

# Copy WSGI config
COPY ./website/lfi_static_resource.wsgi /var/www/teampass/webapp/teampass.wsgi

# Accept flag at build time and inject into configuration
ARG FLAG="FLAG{default_flag_placeholder}"
RUN sed "s|%%FLAG%%|${FLAG}|g" /var/www/teampass/includes/config/tp.config.php.tpl \
    > /var/www/teampass/includes/config/tp.config.php \
    && rm /var/www/teampass/includes/config/tp.config.php.tpl

# Set ownership
RUN chown -R www-data:www-data /var/www/teampass

# Configure Apache
COPY ./lfi_static_resource-httpd.conf /etc/apache2/sites-available/teampass.conf
RUN a2dissite 000-default.conf \
    && a2ensite teampass.conf \
    && a2enmod headers \
    && a2enmod rewrite \
    && a2enmod autoindex

# Remove PHP module if present (we serve .php files as static text - part of the vulnerability)
RUN a2dismod php* 2>/dev/null || true

# Configure Apache to serve .php files as plain text (no PHP interpreter)
RUN echo "RemoveHandler .php" > /etc/apache2/conf-available/no-php.conf \
    && echo "RemoveType .php" >> /etc/apache2/conf-available/no-php.conf \
    && echo "AddType text/plain .php" >> /etc/apache2/conf-available/no-php.conf \
    && a2enconf no-php

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=1s --start-period=5s --retries=5 \
    CMD curl -s -o /dev/null -w "%{http_code}" http://localhost:80/login | grep -q "200" || exit 1

CMD ["/usr/sbin/apache2ctl", "-D", "FOREGROUND"]
