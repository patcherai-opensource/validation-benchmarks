#!/bin/bash
set -e

# If FLAG is set, write it to the secret file
if [ -n "$FLAG" ] && [ "$FLAG" != "FLAG_PLACEHOLDER" ]; then
    echo "$FLAG" > /var/reposilite/configuration/token.secret
    chmod 600 /var/reposilite/configuration/token.secret
    chown www-data:www-data /var/reposilite/configuration/token.secret
fi

# Clear the FLAG from environment before starting Apache
unset FLAG

exec "$@"
