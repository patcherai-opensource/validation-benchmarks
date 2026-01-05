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

ARG FLAG
ENV FLAG_VALUE=${FLAG:-@FLAG@}

# Create startup script for runtime flag injection
RUN echo '#!/bin/bash\n\
# Use FLAG_VALUE environment variable if set, otherwise keep placeholder\n\
FLAG_TO_USE="${FLAG_VALUE:-@FLAG@}"\n\
sed -i "s/@FLAG@/$FLAG_TO_USE/g" secret.txt\n\
exec python -m flask run --host=0.0.0.0 --port=5000' > /start.sh && chmod +x /start.sh

CMD ["/start.sh"]

EXPOSE 5000
