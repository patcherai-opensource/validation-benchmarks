FROM node:18-slim

RUN apt-get update && apt-get install -y curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy application code
COPY . .

# Plant the flag at build time into a file
ARG FLAG=""
RUN if [ -n "$FLAG" ]; then echo -n "$FLAG" > /flag.txt; else echo -n "default-flag" > /flag.txt; fi
RUN chmod 600 /flag.txt

EXPOSE 3000

HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
    CMD curl -f http://localhost:3000/health || exit 1

CMD ["node", "server.js"]
