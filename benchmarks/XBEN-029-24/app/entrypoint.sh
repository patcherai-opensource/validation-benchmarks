#!/bin/bash

if [ -n "$FLAG" ]; then
    echo -n "$FLAG" > /flag.txt
    chmod 644 /flag.txt
fi

exec /usr/bin/supervisord
