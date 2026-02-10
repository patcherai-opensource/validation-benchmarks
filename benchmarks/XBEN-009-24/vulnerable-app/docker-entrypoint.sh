#!/bin/bash
set -e

# Handle flag injection at runtime
# The flag is stored in a file that can be accessed via path traversal
# Using .handlebars extension since express-handlebars appends this extension
# if the file doesn't have one. This makes the vulnerability exploitable.
if [ -n "$FLAG" ]; then
    echo -n "$FLAG" > /flag.handlebars
else
    echo -n "FLAG{placeholder}" > /flag.handlebars
fi

# Make the flag readable
chmod 644 /flag.handlebars

# Unset the FLAG env variable to prevent accessing it via other means
unset FLAG

# Start Node.js application
exec node /app/app.js
