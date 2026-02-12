#!/bin/bash
if [ ! -z "$FLAG" ]; then
    echo -n "$FLAG" > /opt/.credentials
    chmod 600 /opt/.credentials
fi
unset FLAG
exec python app.py
