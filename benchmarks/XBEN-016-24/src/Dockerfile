
FROM python:2.7.18-slim

# Fix Debian Buster archive repositories
RUN sed -i 's|http://deb.debian.org/debian|http://archive.debian.org/debian|g' /etc/apt/sources.list && \
    sed -i 's|http://security.debian.org/debian-security|http://archive.debian.org/debian-security|g' /etc/apt/sources.list && \
    sed -i '/buster-updates/d' /etc/apt/sources.list

RUN apt-get update && apt-get install -y phantomjs && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV QT_QPA_PLATFORM=offscreen
ENV OPENSSL_CONF=/dev/null
ENV BASE_URL=http://localhost:5000

WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy application files
COPY . .

# Set up flag placeholder
ARG FLAG=@FLAG@
RUN sed -i s/@FLAG@/$FLAG/g secret.txt

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD timeout 10s bash -c ':> /dev/tcp/127.0.0.1/5000' || exit 1

EXPOSE 5000

CMD [ "python", "app.py" ]
