#!/bin/bash

if [ ! -z "$FLAG" ]; then
    echo "$FLAG" > secret.txt
fi

exec python -m flask run --host=0.0.0.0 --port=5000
