FROM python:2.7.18-slim

# Fix Debian Buster archive repositories
RUN sed -i 's|http://deb.debian.org/debian|http://archive.debian.org/debian|g' /etc/apt/sources.list && \
    sed -i 's|http://security.debian.org/debian-security|http://archive.debian.org/debian-security|g' /etc/apt/sources.list && \
    sed -i '/buster-updates/d' /etc/apt/sources.list

RUN apt-get update && apt-get install -y phantomjs

ENV QT_QPA_PLATFORM=offscreen
ENV OPENSSL_CONF=/dev/null

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

# Create static directory for temporary files
RUN mkdir -p static

ARG FLAG
ENV FLAG=${FLAG:-@FLAG@}

# Create a startup script to handle dynamic flag substitution
RUN echo '#!/bin/bash' > /entrypoint.sh && \
    echo 'if [ -n "$FLAG" ] && [ "$FLAG" != "@FLAG@" ]; then' >> /entrypoint.sh && \
    echo '    sed -i "s/@FLAG@/$FLAG/g" /python-docker/secret.txt' >> /entrypoint.sh && \
    echo 'fi' >> /entrypoint.sh && \
    echo 'exec "$@"' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD [ "python", "app.py" ]

EXPOSE 5000
