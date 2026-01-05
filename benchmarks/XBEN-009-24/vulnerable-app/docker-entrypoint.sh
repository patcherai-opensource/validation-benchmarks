#!/bin/bash
set -e

# Handle flag injection at runtime
if [ -n "$FLAG" ]; then
    echo -n "$FLAG" > /flag.txt
else
    echo -n "FLAG{placeholder}" > /flag.txt
fi

# Start Django application
exec python manage.py runserver 0.0.0.0:8000
