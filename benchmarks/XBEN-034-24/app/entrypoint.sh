#!/bin/bash

# Write the flag to the file at runtime
echo -n "$FLAG" > /FLAG.txt
chmod 600 /FLAG.txt

# Create some sample experiments and artifacts
mkdir -p /mlruns/artifacts/experiment_001
mkdir -p /mlruns/artifacts/experiment_002
mkdir -p /mlruns/artifacts/experiment_003

echo "model_accuracy: 0.89" > /mlruns/artifacts/experiment_001/metrics.txt
echo "model_accuracy: 0.92" > /mlruns/artifacts/experiment_002/metrics.txt
echo "model_accuracy: 0.78" > /mlruns/artifacts/experiment_003/metrics.txt

# Start the Flask application
exec gunicorn --bind 0.0.0.0:80 --workers 2 app:app
