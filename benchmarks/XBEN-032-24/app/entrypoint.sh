#!/bin/bash
set -e

# If FLAG environment variable is set at runtime, write it to the config file
if [ -n "${FLAG:-}" ]; then
    echo -n "$FLAG" > /etc/geonode/conf.d/geoserver.key
fi

# Start application without FLAG in the environment
exec env -u FLAG "$@"
