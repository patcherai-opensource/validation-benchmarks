#!/bin/sh
set -e

# Start the application server with gunicorn (single worker to keep PID predictable)
exec gunicorn --bind 0.0.0.0:8080 \
    --workers 1 \
    --timeout 120 \
    --access-logfile /dev/null \
    --error-logfile /dev/stderr \
    --log-level warning \
    server:app
