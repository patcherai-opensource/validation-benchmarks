
FROM python:2.7.18-slim

# Fix Debian Buster archive repositories
RUN sed -i 's|http://deb.debian.org/debian|http://archive.debian.org/debian|g' /etc/apt/sources.list && \
    sed -i 's|http://security.debian.org/debian-security|http://archive.debian.org/debian-security|g' /etc/apt/sources.list && \
    sed -i '/buster-updates/d' /etc/apt/sources.list


RUN apt-get update && apt-get install -y phantomjs

ENV QT_QPA_PLATFORM=offscreen
ENV OPENSSL_CONF=/dev/null
ENV FLASK_ENV=production

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

ARG FLAG
ENV FLAG=${FLAG:-@FLAG@}

# Create startup script that plants the flag into the secret file at runtime
# and then removes the environment variable
RUN echo '#!/bin/bash' > /entrypoint.sh && \
    echo 'if [ -n "$FLAG" ] && [ "$FLAG" != "@FLAG@" ]; then' >> /entrypoint.sh && \
    echo '    echo -n "$FLAG" > /python-docker/secret.txt' >> /entrypoint.sh && \
    echo '    unset FLAG' >> /entrypoint.sh && \
    echo 'fi' >> /entrypoint.sh && \
    echo 'exec "$@"' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

RUN mkdir -p /python-docker/static

ENTRYPOINT ["/entrypoint.sh"]
CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0", "--port=5000"]

EXPOSE 5000
