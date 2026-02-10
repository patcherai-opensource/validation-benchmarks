#!/bin/bash

# Start Apache
# Note: Flag is written at build time to /flag, not from environment variable
exec /usr/sbin/apache2ctl -D FOREGROUND
