<?php
$hash = password_hash('admin', PASSWORD_BCRYPT);
$sql = file_get_contents('/app/db_init.sql');
$sql = str_replace('$ADMIN_HASH$', $hash, $sql);
file_put_contents('/app/db_init.sql', $sql);
echo "Password hash generated and injected.\n";
