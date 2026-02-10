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

# Support build-time flag injection
ARG FLAG=""
RUN if [ -n "$FLAG" ]; then echo "$FLAG" > secret.txt; fi

# Also support runtime environment variable for flag injection (k8s)
ENV FLAG=""

RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]

EXPOSE 5000
