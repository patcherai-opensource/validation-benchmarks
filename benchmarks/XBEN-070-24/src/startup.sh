#!/bin/bash

# Handle flag: runtime env var takes precedence, then build-time, then placeholder replacement
if [ ! -z "$FLAG" ]; then
    # Runtime FLAG environment variable - write directly to secret.txt
    echo "$FLAG" > secret.txt
elif [ ! -z "$FLAG_BUILD" ] && [ "$FLAG_BUILD" != "" ]; then
    # Build-time FLAG was used - already in secret.txt, do nothing
    :
else
    # Neither provided - keep @FLAG@ placeholder or existing content
    :
fi

# Start the Flask application
exec python -m flask run --host=0.0.0.0 --port=5000
