#!/bin/bash

# Create the FLAG.php file with the runtime flag value
echo "<?php \$flag = \"$FLAG\"; ?>" > /FLAG.php

# Execute the original command
exec "$@"