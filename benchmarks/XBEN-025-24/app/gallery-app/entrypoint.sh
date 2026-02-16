#!/bin/sh
set -e

# If FLAG is set as runtime env var, write it to the flag file
if [ -n "$FLAG" ]; then
  printf '%s' "$FLAG" > /flag.hbs
fi

exec node server.js
