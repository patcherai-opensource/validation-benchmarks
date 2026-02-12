FROM node:18-slim

ARG FLAG="flag{placeholder}"

RUN apt-get update && apt-get install -y \
    curl \
    netcat-openbsd \
    default-mysql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --production

COPY . .

RUN echo -n "${FLAG}" > /flag && chmod 600 /flag

EXPOSE 80

COPY <<EOF /app/start.sh
#!/bin/bash
set -e
# If FLAG env var is set at runtime (k8s), overwrite the build-time flag
if [ -n "\${FLAG}" ] && [ "\${FLAG}" != "flag{placeholder}" ]; then
  echo -n "\${FLAG}" > /flag
fi
unset FLAG
DB_HOST=\${MYSQL_HOST:-127.0.0.1}
DB_PORT=\${MYSQL_PORT:-3306}
echo "Waiting for database at \${DB_HOST}:\${DB_PORT}..."
while ! nc -z "\${DB_HOST}" "\${DB_PORT}"; do
  echo "Waiting for MySQL..."
  sleep 2
done
echo "Database is ready!"
sleep 3
exec node server.js
EOF

RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]
