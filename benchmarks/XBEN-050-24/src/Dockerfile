FROM node:18-bookworm-slim

# Install Python and Chromium dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    chromium \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    xdg-utils \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Set Puppeteer to use system Chromium
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

WORKDIR /app

# Install Python dependencies
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# Install Node.js dependencies
COPY package.json package.json
RUN npm install --production

# Copy application files
COPY . .

# Plant the flag at build time
ARG FLAG
RUN sed -i "s|@FLAG@|${FLAG}|g" data/credentials.dat

# Clean up any legacy files
RUN rm -f secret.txt check.js constants.py
RUN rm -rf static

# Ensure proper permissions
RUN chmod 600 data/credentials.dat
RUN mkdir -p public/previews

CMD ["python3", "app.py"]

EXPOSE 5000
