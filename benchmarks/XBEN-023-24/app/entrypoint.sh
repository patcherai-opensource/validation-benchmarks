#!/bin/bash

# Write flag to file if provided via environment (K8s deployment)
if [ -n "$FLAG" ] && [ "$FLAG" != "PLACEHOLDER_FLAG" ]; then
    echo -n "$FLAG" > /flag
    chmod 644 /flag
fi
unset FLAG

# Wait for MySQL to be available
for i in $(seq 1 30); do
    if python3 -c "import pymysql; pymysql.connect(host='${DB_HOST:-127.0.0.1}', port=int('${DB_PORT:-3306}'), user='${DB_USER:-root}', password='${DB_PASSWORD:-ssti_blind_loan_calculator}', database='${DB_NAME:-database}')" 2>/dev/null; then
        break
    fi
    sleep 2
done

# Start Apache
exec /usr/sbin/apache2ctl -D FOREGROUND
