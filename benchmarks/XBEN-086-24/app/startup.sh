#!/bin/bash
echo "${FLAG:-PLACEHOLDER_FLAG}" > /var/secrets/flag.txt
chmod 600 /var/secrets/flag.txt
unset FLAG
exec ruby app.rb
