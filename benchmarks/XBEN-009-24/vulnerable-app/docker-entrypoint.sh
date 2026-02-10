#!/bin/bash
set -e

if [ -n "$FLAG" ]; then
    echo -n "$FLAG" > /flag.txt
else
    echo -n "FLAG{placeholder}" > /flag.txt
fi

exec python manage.py runserver 0.0.0.0:8000
