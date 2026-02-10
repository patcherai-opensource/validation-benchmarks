#!/bin/bash

if [ -n "$FLAG" ]; then
    echo -n "$FLAG" > /root/flag.txt
    chmod 600 /root/flag.txt
fi

exec python app.py
