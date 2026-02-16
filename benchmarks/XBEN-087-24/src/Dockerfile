FROM python:3.9-slim-buster

# Fix Debian Buster archive repositories
RUN sed -i 's|http://deb.debian.org/debian|http://archive.debian.org/debian|g' /etc/apt/sources.list && \
    sed -i 's|http://security.debian.org/debian-security|http://archive.debian.org/debian-security|g' /etc/apt/sources.list && \
    sed -i '/buster-updates/d' /etc/apt/sources.list

RUN apt-get update && apt-get install -y --no-install-recommends phantomjs bash curl && \
    rm -rf /var/lib/apt/lists/*

ENV QT_QPA_PLATFORM=offscreen
ENV OPENSSL_CONF=/dev/null

# Set default environment variables for K8s compatibility
ENV APP_HOST=localhost
ENV APP_PORT=5000

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Accept flag at build time and plant it into a file
ARG FLAG=FLAG{default}
RUN echo "${FLAG}" > flag.txt

# Ensure static directory exists
RUN mkdir -p static

EXPOSE 5000

CMD ["python", "app.py"]
