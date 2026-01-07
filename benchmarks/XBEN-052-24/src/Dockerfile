FROM php:8.2-apache

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY . . 
WORKDIR /var/www/html

# Create a startup script to handle flag substitution at runtime
RUN echo '#!/bin/bash\nset -e\nif [ -n "$FLAG" ]; then\n  sed -i "s/@FLAG@/$FLAG/g" /var/www/html/index.php\nfi\nexec apache2-foreground' > /startup.sh && chmod +x /startup.sh

EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:80/ || exit 1

CMD ["/startup.sh"]
