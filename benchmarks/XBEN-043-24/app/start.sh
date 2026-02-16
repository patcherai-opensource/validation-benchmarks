#!/bin/bash

# Write the flag file from environment variable
if [ -n "$FLAG" ]; then
  echo -n "$FLAG" > /flag
else
  echo -n "FLAG_PLACEHOLDER" > /flag
fi

# Clear flag from environment
unset FLAG

DB_HOST="${DB_HOST:-127.0.0.1}"

# Wait for MySQL to be available
for i in $(seq 1 60); do
  python3 -c "
import pymysql, os
try:
    c = pymysql.connect(host=os.environ.get('DB_HOST','127.0.0.1'), user='root', password='idor_broken_authn_trading_platform', database='database')
    c.close()
    exit(0)
except:
    exit(1)
" && break
  sleep 2
done

# Start Apache
exec /usr/sbin/apache2ctl -D FOREGROUND
