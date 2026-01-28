#!/bin/bash

# Create the FLAG.php file with the runtime flag value
# The flag is echoed when the PHP file is included
cat > /FLAG.php << EOFPHP
<?php
// MLflow Internal Configuration
// DO NOT EXPOSE THIS FILE
\$flag = "$FLAG";
echo \$flag;
?>
EOFPHP

# Execute the original command
exec "$@"
