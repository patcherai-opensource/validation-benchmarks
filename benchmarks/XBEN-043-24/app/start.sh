#!/bin/bash
set -e
DB_HOST="${DB_HOST:-127.0.0.1}"
for i in $(seq 1 60); do
  python3 -c "
import pymysql, os
pymysql.connect(
    host=os.environ.get('DB_HOST','127.0.0.1'),
    user='root',
    password='superset_analytics_db',
    database='database'
)
" 2>/dev/null && break
  sleep 2
done
exec /usr/sbin/apache2ctl -D FOREGROUND
