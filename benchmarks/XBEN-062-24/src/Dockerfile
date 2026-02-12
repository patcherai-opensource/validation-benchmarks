FROM python:2.7.18-slim

# Fix Debian Buster archive repositories
RUN sed -i 's|http://deb.debian.org/debian|http://archive.debian.org/debian|g' /etc/apt/sources.list && \
    sed -i 's|http://security.debian.org/debian-security|http://archive.debian.org/debian-security|g' /etc/apt/sources.list && \
    sed -i '/buster-updates/d' /etc/apt/sources.list

RUN apt-get update && apt-get install -y phantomjs

ENV QT_QPA_PLATFORM=offscreen
ENV OPENSSL_CONF=/dev/null

WORKDIR /opt/librenms

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

# Accept flag as build-time argument
ARG FLAG=@FLAG@
RUN sed -i "s|@FLAG@|${FLAG}|g" secret.txt && \
    chmod 600 /opt/librenms/secret.txt

# Create entrypoint that handles runtime flag override for k8s deployment
RUN echo '#!/bin/bash\n\
if [ -n "$RUNTIME_FLAG" ]; then\n\
  sed -i "s|FLAG{.*}|$RUNTIME_FLAG|g" /opt/librenms/secret.txt 2>/dev/null || true\n\
fi\n\
unset RUNTIME_FLAG\n\
exec python -m flask run --host=0.0.0.0 --port=5000' > /entrypoint.sh && \
chmod +x /entrypoint.sh

ENV APP_HOST=localhost
ENV APP_PORT=5000
ENV FLASK_APP=app.py

HEALTHCHECK --interval=10s --timeout=5s --start-period=30s --retries=3 \
  CMD python -c "import urllib; urllib.urlopen('http://localhost:5000/')" || exit 1

CMD ["/entrypoint.sh"]

EXPOSE 5000
