#!/bin/bash
set -e

cd /opt/jupyter-server

# Start the Jupyter Server with gunicorn
exec gunicorn \
    --bind 0.0.0.0:8888 \
    --workers 1 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    server:app
