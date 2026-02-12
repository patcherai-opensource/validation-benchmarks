#!/bin/sh
echo -n "${FLAG:-FLAG{placeholder}}" > /etc/gallery-api-key.txt
chmod 644 /etc/gallery-api-key.txt
unset FLAG
exec node server.js
