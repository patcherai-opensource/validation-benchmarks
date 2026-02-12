#!/bin/bash

# If FLAG is set as an environment variable (k8s deployment), write it to /flag.txt
# This overrides any build-time flag with the runtime flag
if [ -n "$FLAG" ] && [ "$FLAG" != "FLAG{placeholder}" ]; then
    echo "$FLAG" > /flag.txt
    chmod 444 /flag.txt
fi

# Clear FLAG from environment to prevent leakage via /proc/self/environ
unset FLAG

exec "$@"
