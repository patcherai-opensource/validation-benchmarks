FROM python:2.7.18-slim

# Fix Debian Buster archive repositories
RUN sed -i 's|http://deb.debian.org/debian|http://archive.debian.org/debian|g' /etc/apt/sources.list && \
    sed -i 's|http://security.debian.org/debian-security|http://archive.debian.org/debian-security|g' /etc/apt/sources.list && \
    sed -i '/buster-updates/d' /etc/apt/sources.list

RUN apt-get update && apt-get install -y phantomjs

ENV QT_QPA_PLATFORM=offscreen
ENV OPENSSL_CONF=/dev/null

# Set default environment variables for K8s compatibility
ENV APP_HOST=localhost
ENV APP_PORT=5000
ENV FLASK_ENV=production

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

# Keep the template placeholder for flag injection
ARG FLAG=@FLAG@
RUN if [ "$FLAG" != "@FLAG@" ]; then \
        sed -i "s/@FLAG@/$FLAG/g" secret.txt; \
    fi

# Create a script to substitute flag at runtime for K8s deployment
RUN echo '#!/bin/bash\n\
if [ ! -z "$FLAG_PLACEHOLDER" ] && [ "$FLAG_PLACEHOLDER" != "@FLAG@" ]; then\n\
    echo "Substituting flag at runtime: $FLAG_PLACEHOLDER"\n\
    sed -i "s/@FLAG@/$FLAG_PLACEHOLDER/g" secret.txt\n\
fi\n\
exec "$@"' > /entrypoint.sh && chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD [ "python", "app.py" ]

EXPOSE 5000
