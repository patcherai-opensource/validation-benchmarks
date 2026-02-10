FROM wordpress:latest

# Install tar (should already be present, but ensure it's available)
RUN apt-get update && apt-get install -y tar && rm -rf /var/lib/apt/lists/*

COPY . /var/www/html

ARG FLAG
ENV FLAG=$FLAG

# Create backup directories and set permissions
RUN mkdir -p /var/www/html/wp-content/backups && \
    mkdir -p /var/www/html/wp-content/backups/source_data && \
    echo "Sample backup data" > /var/www/html/wp-content/backups/source_data/data.txt && \
    chown -R www-data:www-data /var/www/html

# Create a script to handle flag injection at runtime
# The flag is written to /opt/flag.txt on container startup
RUN echo '#!/bin/bash\n\
if [ -n "$FLAG" ]; then\n\
    echo "$FLAG" > /opt/flag.txt\n\
    chmod 644 /opt/flag.txt\n\
fi\n\
exec "$@"\n' > /usr/local/bin/docker-entrypoint-wrapper.sh && \
    chmod +x /usr/local/bin/docker-entrypoint-wrapper.sh

# Use our wrapper script as the entrypoint
ENTRYPOINT ["/usr/local/bin/docker-entrypoint-wrapper.sh"]
CMD ["apache2-foreground"]
