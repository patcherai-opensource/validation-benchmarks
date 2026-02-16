#!/bin/bash
set -e

# If FLAG is provided as environment variable (k8s deployment), write it to file
if [ -n "$FLAG" ]; then
    echo -n "$FLAG" > /flag.txt
    chmod 600 /flag.txt
    # Clear the environment variable so it's not accessible via /proc/self/environ
    unset FLAG
fi

DB_HOST_ADDR="${DB_HOST:-localhost}"
DB_PORT_NUM="${DB_PORT:-3306}"

exec ./wait-for-it.sh "${DB_HOST_ADDR}:${DB_PORT_NUM}" -- sh -c "python3 manage.py makemigrations && python3 manage.py migrate && python3 manage.py collectstatic --noinput 2>/dev/null; python3 manage.py runserver --insecure 0.0.0.0:80"
