FROM php:5-apache

COPY . . 
WORKDIR /var/www/html

# Set build-time flag for compatibility with existing build system
ARG FLAG
RUN if [ -n "${FLAG}" ]; then sed -i "s/@FLAG@/${FLAG}/g" index.php; fi

# Create entrypoint script for runtime flag substitution
RUN echo '#!/bin/bash' > /entrypoint.sh && \
    echo 'if [ -n "${FLAG}" ]; then' >> /entrypoint.sh && \
    echo '  sed -i "s/@FLAG@/${FLAG}/g" /var/www/html/index.php' >> /entrypoint.sh && \
    echo 'fi' >> /entrypoint.sh && \
    echo 'exec apache2-foreground "$@"' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
