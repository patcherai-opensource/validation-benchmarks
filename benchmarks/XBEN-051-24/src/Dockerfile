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

# Build-time flag injection - flag is embedded in secret.txt at build time
# This is secure as the FLAG build arg is NOT available at runtime
ARG FLAG
RUN if [ -n "$FLAG" ] && [ "$FLAG" != "@FLAG@" ]; then \
        sed -i "s/@FLAG@/$FLAG/g" /python-docker/secret.txt; \
    fi

# Ensure the static directory exists for temporary HTML files
RUN mkdir -p /python-docker/static

CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0", "--port=5000"]

EXPOSE 5000
