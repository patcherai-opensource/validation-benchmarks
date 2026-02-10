FROM node:18-slim

WORKDIR /app

# Install curl for healthchecks
RUN apt-get update -y && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy package files and install dependencies
COPY package.json /app/
RUN npm install

# Copy application files
COPY app.js /app/
COPY views /app/views/

# Create public directory for static files
RUN mkdir -p /app/public

# Create entrypoint script for runtime flag injection
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["docker-entrypoint.sh"]
