FROM php:7.4-apache

ARG FLAG

RUN apt-get update -y && \
    apt-get install -y curl libcurl4-openssl-dev pkg-config && \
    docker-php-ext-install curl && \
    a2enmod rewrite && \
    sed -i '/<Directory \/var\/www\/>/,/<\/Directory>/ s/AllowOverride None/AllowOverride All/' /etc/apache2/apache2.conf && \
    rm -rf /var/lib/apt/lists/*

COPY . /var/www/html/

RUN mkdir -p /opt/axis/conf /opt/axis/attachments && \
    echo "# Axis Service Credentials" > /opt/axis/conf/users.lst && \
    echo "# Format: username=password" >> /opt/axis/conf/users.lst && \
    echo "admin=axis" >> /opt/axis/conf/users.lst && \
    echo "" >> /opt/axis/conf/users.lst && \
    echo "# Service deployment key" >> /opt/axis/conf/users.lst && \
    echo "# ${FLAG}" >> /opt/axis/conf/users.lst && \
    chmod 600 /opt/axis/conf/users.lst && \
    chown www-data:www-data /opt/axis/conf/users.lst

RUN echo 'ServerTokens Prod' >> /etc/apache2/apache2.conf && \
    echo 'ServerSignature Off' >> /etc/apache2/apache2.conf

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=1s --start-period=5s --retries=5 \
    CMD curl -f http://localhost/ || exit 1
