
FROM python:2.7.18-slim

# Fix Debian Buster archive repositories
RUN sed -i 's|http://deb.debian.org/debian|http://archive.debian.org/debian|g' /etc/apt/sources.list && \
    sed -i 's|http://security.debian.org/debian-security|http://archive.debian.org/debian-security|g' /etc/apt/sources.list && \
    sed -i '/buster-updates/d' /etc/apt/sources.list

RUN apt-get update && apt-get install -y phantomjs bash

ENV QT_QPA_PLATFORM=offscreen
ENV OPENSSL_CONF=/dev/null

# Set default environment variables for K8s compatibility
ENV APP_HOST=localhost
ENV APP_PORT=5000

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

RUN mkdir -p static

# Create an entrypoint script to handle flag substitution at runtime
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]

EXPOSE 5000
