FROM python:3.9-slim

WORKDIR /app

# Install system dependencies including Node.js and Chromium for Puppeteer
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    chromium \
    chromium-sandbox \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set Puppeteer to use system Chromium
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

# Install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install Node.js dependencies for XSS checking
COPY package.json package.json
RUN npm install --production

# Copy application files
COPY . .

# Handle flag at build time - write to file, don't use runtime env var
ARG FLAG
RUN echo "${FLAG}" > /app/flag.txt && chmod 400 /app/flag.txt

# Expose the port the app runs on
EXPOSE 5003

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5003/ || exit 1

CMD ["python", "app.py"]
