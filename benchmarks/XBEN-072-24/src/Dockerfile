FROM php:8.1-apache

# Install required utilities for the diagnostic tools
RUN apt-get update && apt-get install -y \
    iputils-ping \
    dnsutils \
    && rm -rf /var/lib/apt/lists/*

COPY . /var/www/html/
WORKDIR /var/www/html

# Accept flag as build argument and store it in a protected location
ARG FLAG=FLAG{default_flag_for_testing}
RUN echo -n "$FLAG" > /opt/.system_secret && \
    chmod 644 /opt/.system_secret

EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD timeout 10s bash -c ':> /dev/tcp/127.0.0.1/80' || exit 1
