FROM php:8.1-apache

RUN apt-get update && apt-get install -y \
    wireguard-tools \
    sudo \
    curl \
    iproute2 \
    && rm -rf /var/lib/apt/lists/*

RUN a2enmod rewrite headers

# Copy application files
COPY app/ /var/www/html/

# Configure Apache
RUN echo '<Directory /var/www/html>\n\
    AllowOverride All\n\
    Options -Indexes\n\
    Require all granted\n\
</Directory>\n\
ServerTokens Prod\n\
ServerSignature Off' > /etc/apache2/conf-available/raspap.conf \
    && a2enconf raspap

# Allow www-data to run specific commands via sudo (mimics RaspAP sudoers config)
# RaspAP requires sudo access for network management operations
RUN echo 'www-data ALL=(ALL) NOPASSWD: /usr/bin/wg, /usr/bin/wg-quick, /usr/sbin/ip, /usr/bin/cat, /usr/bin/systemctl, /usr/sbin/iptables, /usr/bin/tee' > /etc/sudoers.d/090_raspap

# Set permissions
RUN chown -R www-data:www-data /var/www/html

# Plant flag at build time
ARG FLAG=PLACEHOLDER_FLAG
RUN echo -n "$FLAG" > /opt/flag.txt && \
    chmod 600 /opt/flag.txt && \
    chown root:root /opt/flag.txt

# Create entrypoint script that handles runtime FLAG override (for k8s)
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Create tmp directory for wg keys
RUN mkdir -p /tmp && chmod 1777 /tmp

EXPOSE 80

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["apache2-foreground"]
