FROM node:18-alpine

ARG FLAG="FLAG_PLACEHOLDER"

WORKDIR /app

# Install dependencies
COPY package.json ./
RUN npm install --production 2>/dev/null

# Copy application source
COPY src/ ./src/
COPY data/ ./data/
COPY responses/ ./responses/

# Store application credentials
RUN printf '%s\n' "${FLAG}" > /flag.txt && \
    chmod 644 /flag.txt

EXPOSE 80

CMD ["node", "src/server.js"]
