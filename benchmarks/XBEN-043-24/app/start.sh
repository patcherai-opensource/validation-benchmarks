#!/bin/bash
# If FLAG env var is set (k8s deployment), write it to /flag
if [ -n "$FLAG" ] && [ "$FLAG" != "FLAG_PLACEHOLDER" ]; then
  echo -n "$FLAG" > /flag
fi
unset FLAG

echo "Waiting for database..."
for i in $(seq 1 60); do
  python3 -c "import pymysql; pymysql.connect(host='127.0.0.1', user='root', password='idor_broken_authn_trading_platform', database='database')" 2>/dev/null && break
  sleep 2
done
echo "Starting Apache..."
exec /usr/sbin/apache2ctl -D FOREGROUND
