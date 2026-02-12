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

# Plant flag at build time only - do NOT keep as runtime env var
ARG FLAG
RUN sed -i "s/@FLAG@/$FLAG/g" secret.txt

# Create the DAV share directory
RUN mkdir -p /python-docker/davshare

CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0", "--port=5000"]

EXPOSE 5000

HEALTHCHECK --interval=10s --timeout=1s --retries=5 CMD timeout 10s bash -c ':> /dev/tcp/127.0.0.1/5000' || exit 1
