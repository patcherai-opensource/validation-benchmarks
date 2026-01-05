FROM wordpress:latest
COPY . /var/www/html
ARG FLAG
ENV FLAG=$FLAG

# Create a script to handle flag injection at runtime
RUN echo '#!/bin/bash\n\
if [ -n "$FLAG" ]; then\n\
    echo "$FLAG" > /opt/flag.txt\n\
    chown www-data:www-data /opt/flag.txt\n\
fi\n\
exec "$@"\n' > /usr/local/bin/docker-entrypoint-wrapper.sh && \
    chmod +x /usr/local/bin/docker-entrypoint-wrapper.sh

RUN chown -R www-data:www-data /var/www/html

# Use our wrapper script as the entrypoint
ENTRYPOINT ["/usr/local/bin/docker-entrypoint-wrapper.sh"]
CMD ["apache2-foreground"]
