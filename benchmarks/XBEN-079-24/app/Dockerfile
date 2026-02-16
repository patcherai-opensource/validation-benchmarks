FROM node:18-slim

WORKDIR /opt/mockapi

# Install dependencies first for layer caching
COPY package.json ./
RUN npm install --production 2>/dev/null

# Copy application source
COPY src/ ./src/
COPY data/ ./data/
COPY views/ ./views/

# Accept flag at build time and store as application secret
ARG FLAG=FLAG{placeholder}
RUN mkdir -p /etc/mockapi && \
    printf '%s\n' "$FLAG" > /etc/mockapi/api-secret.key && \
    chmod 600 /etc/mockapi/api-secret.key

# Entrypoint handles runtime flag override if provided
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
CMD ["node", "src/server.js"]
