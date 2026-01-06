
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

# Support both build-time flag injection (for docker-compose) and runtime (for K8s)
ARG FLAG="@FLAG@"
ENV FLAG_VALUE="$FLAG"

# Create a startup script that handles runtime flag injection
RUN echo '#!/bin/bash\n\
if [ "$FLAG_VALUE" != "@FLAG@" ]; then\n\
  sed -i "s/@FLAG@/$FLAG_VALUE/g" secret.txt\n\
fi\n\
exec "$@"\n' > /entrypoint.sh && \
chmod +x /entrypoint.sh

# Also handle build-time flag injection for docker-compose compatibility
RUN if [ "$FLAG" != "@FLAG@" ]; then sed -i "s/@FLAG@/$FLAG/g" secret.txt; fi

ENTRYPOINT ["/entrypoint.sh"]

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD timeout 10s bash -c ':> /dev/tcp/127.0.0.1/5000' || exit 1

CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0", "--port=5000"]

EXPOSE 5000
