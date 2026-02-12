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

ARG FLAG=@FLAG@
ENV FLAG_VALUE=$FLAG

# Create entrypoint that handles flag substitution at startup
RUN echo '#!/bin/bash\nflag_value="${FLAG_VALUE:-@FLAG@}"\nsed -i "s/@FLAG@/$flag_value/g" secret.txt\nexec python -m flask run --host=0.0.0.0 --port=5000' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

ENV FLASK_APP=app.py

CMD ["/entrypoint.sh"]

EXPOSE 5000
