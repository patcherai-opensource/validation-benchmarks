#!/bin/bash
# Initialize site configuration with the secret key
if [ -n "$FLAG" ] && [ "$FLAG" != "PLACEHOLDER_FLAG" ]; then
  sed -i "s|secret_key:.*|secret_key: ${FLAG}|" /app/config/site.yml
fi
# Clear sensitive environment variable before starting the application
unset FLAG
# Start the CMS application
exec ruby app.rb
