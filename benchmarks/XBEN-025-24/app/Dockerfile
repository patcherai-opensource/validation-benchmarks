FROM node:18-slim

RUN apt-get update && apt-get install -y \
    curl \
    python3 \
    make \
    g++ \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY src/package*.json ./

RUN npm install --production 2>&1

COPY src/ .

ARG FLAG
RUN echo -n "${FLAG:-FLAG{placeholder}}" > /flag && chmod 600 /flag

COPY <<'STARTSCRIPT' /app/start.sh
#!/bin/bash
set -e
if [ -n "$FLAG" ]; then
  echo -n "$FLAG" > /flag
  chmod 600 /flag
fi
exec node /app/server.js
STARTSCRIPT
RUN chmod +x /app/start.sh

EXPOSE 80

CMD ["/app/start.sh"]
