#!/bin/sh
# Clear any runtime environment variables that shouldn't be accessible
unset FLAG
exec "$@"
