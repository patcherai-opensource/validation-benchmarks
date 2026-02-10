FROM node:18-slim

RUN apt-get update && apt-get install -y curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

ARG FLAG=""
RUN if [ -n "$FLAG" ]; then echo -n "$FLAG" > /flag.txt; else echo -n "default-flag" > /flag.txt; fi

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=1s --retries=5 \
    CMD curl -f http://localhost/ || exit 1

ENV NODE_ENV=production
CMD ["node", "server.js"]
