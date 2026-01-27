#!/bin/bash
set -e

# FLAG is passed via environment variable and read by PHP at runtime
# No need for file modification

# Execute the original command
exec "$@"
