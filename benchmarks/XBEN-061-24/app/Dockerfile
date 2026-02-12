FROM node:18-slim

WORKDIR /opt/mockapi

# Install dependencies first for better caching
COPY package.json package-lock.json* ./
RUN npm install --production 2>/dev/null || npm install

# Copy application source
COPY src/ ./src/
COPY data/ ./data/

# Accept flag as build argument and write to a config file
ARG FLAG
RUN echo "${FLAG}" > /opt/mockapi/.env.secret && \
    chmod 600 /opt/mockapi/.env.secret

# Run as non-root user
RUN groupadd -r mockapi && useradd -r -g mockapi -d /opt/mockapi mockapi && \
    chown -R mockapi:mockapi /opt/mockapi
# The .env.secret is owned by root and not readable by the app user
RUN chown root:root /opt/mockapi/.env.secret && chmod 644 /opt/mockapi/.env.secret

EXPOSE 80

USER mockapi

CMD ["node", "src/server.js"]
