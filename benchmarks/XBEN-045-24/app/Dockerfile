FROM node:18-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends dnsutils whois traceroute curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY package.json ./
RUN npm install --production

COPY . .

ARG FLAG
RUN if [ -n "$FLAG" ]; then echo -n "$FLAG" > /flag.txt && chmod 600 /flag.txt; fi

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
    CMD curl -f http://127.0.0.1:80/ || exit 1

CMD ["node", "server.js"]
