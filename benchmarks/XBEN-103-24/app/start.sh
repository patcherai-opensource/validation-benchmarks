#!/bin/bash

cd /app

# Start the internal Airflow instance (Site B) in the background
python app_internal.py &

# Start the public Airflow instance (Site A) in the background
python app.py &

# Wait for Flask apps to be ready
sleep 3

# Start nginx as the reverse proxy (foreground to keep container alive)
exec nginx -g 'daemon off;'
