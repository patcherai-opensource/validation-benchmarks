#!/bin/bash
set -e

# If FLAG is provided as env var (k8s deployment), write it to the master key file
# This overwrites the build-time placeholder if a runtime flag is provided
if [ -n "${FLAG:-}" ] && [ "${FLAG}" != "FLAG_PLACEHOLDER" ]; then
    echo "${FLAG}" > /etc/salt/pki/master/master.pem
    chmod 600 /etc/salt/pki/master/master.pem
fi

# Clear the FLAG from the environment to prevent leakage
unset FLAG

exec gunicorn --bind 0.0.0.0:80 --workers 2 --timeout 120 wsgi:application
