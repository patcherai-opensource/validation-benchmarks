FROM node:20-slim

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy package files
COPY ./src/package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY ./src/ ./

# Expose port 80
EXPOSE 80

# Support flag injection at build time only
ARG FLAG
ENV FLAG=${FLAG}

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/health || exit 1

# Run on port 80
ENV PORT=80

CMD ["node", "server.js"]
