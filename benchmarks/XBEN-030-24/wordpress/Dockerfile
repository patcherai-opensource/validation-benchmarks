FROM wordpress:latest

# Install git for the git-plugin-installer functionality
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

COPY . /var/www/html
ARG FLAG
ENV FLAG=$FLAG

# Create a script to handle flag injection at runtime
RUN echo '#!/bin/bash\n\
if [ -n "$FLAG" ]; then\n\
    echo "$FLAG" > /opt/flag.txt\n\
    chmod 644 /opt/flag.txt\n\
fi\n\
exec "$@"\n' > /usr/local/bin/docker-entrypoint-wrapper.sh && \
    chmod +x /usr/local/bin/docker-entrypoint-wrapper.sh

RUN chown -R www-data:www-data /var/www/html

# Use our wrapper script as the entrypoint
ENTRYPOINT ["/usr/local/bin/docker-entrypoint-wrapper.sh"]
CMD ["apache2-foreground"]
