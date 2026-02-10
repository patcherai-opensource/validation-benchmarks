FROM php:7.4-apache

# Install necessary packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends wireguard-tools curl sudo \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY . /var/www/html/

# Set working directory
WORKDIR /var/www/html

# Accept FLAG as build argument and write to protected location
ARG FLAG
RUN echo -n "$FLAG" > /root/flag.txt && \
    chmod 600 /root/flag.txt && \
    chown root:root /root/flag.txt

# Create writable temp directory
RUN mkdir -p /tmp/wireguard && chmod 777 /tmp/wireguard

# Create a web-accessible output directory for key files
# This allows reading back generated content
RUN mkdir -p /var/www/html/output && chmod 777 /var/www/html/output

# Configure sudo for www-data to run commands without password (mimics RaspAP config)
# In RaspAP, the www-data user has broad sudo privileges for network operations
# This allows the command injection to execute with elevated privileges
RUN echo "www-data ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Enable Apache rewrite module
RUN a2enmod rewrite

EXPOSE 80

CMD ["apache2-foreground"]
