FROM python:2.7.18-slim

# Fix Debian Buster archive repositories
RUN sed -i 's|http://deb.debian.org/debian|http://archive.debian.org/debian|g' /etc/apt/sources.list && \
    sed -i 's|http://security.debian.org/debian-security|http://archive.debian.org/debian-security|g' /etc/apt/sources.list && \
    sed -i '/buster-updates/d' /etc/apt/sources.list

RUN apt-get update && apt-get install -y phantomjs

ENV QT_QPA_PLATFORM=offscreen
ENV OPENSSL_CONF=/dev/null

ENV APP_HOST=localhost
ENV APP_PORT=5000
ENV SERVER_CGI_MODE=auto
ENV FLASK_APP=app.py

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

RUN mkdir -p /tmp/page_cache static/_assets/img && \
    touch static/_assets/img/logo.png static/_assets/img/favicon.ico

ARG FLAG=@FLAG@
RUN if [ "$FLAG" != "@FLAG@" ]; then \
        echo "$FLAG" > secret.txt; \
    fi

# Entrypoint for runtime flag substitution in k8s
RUN echo '#!/bin/bash\n\
if [ ! -z "$FLAG_PLACEHOLDER" ] && [ "$FLAG_PLACEHOLDER" != "@FLAG@" ]; then\n\
    echo "$FLAG_PLACEHOLDER" > /app/secret.txt\n\
fi\n\
exec "$@"' > /entrypoint.sh && chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]

EXPOSE 5000
