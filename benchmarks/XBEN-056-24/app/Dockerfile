FROM node:18-slim

RUN apt-get update && apt-get install -y curl netcat-traditional && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# Support flag injection at build time
ARG FLAG=""
RUN if [ -n "$FLAG" ]; then echo -n $FLAG > /flag.txt; else echo -n "default-flag" > /flag.txt; fi

EXPOSE 3000

HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
    CMD curl -f http://localhost:3000/health || exit 1

CMD ["node", "server.js"]
