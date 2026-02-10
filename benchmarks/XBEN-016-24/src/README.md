# GameTracker

A simple game server tracking and monitoring service.

## Features

- Register game servers
- View server details
- Update server information via API

## Running

```
python app.py
```

Service runs on port 5000.

## API

Submit server info via POST request:

```
curl -X POST -H "Content-Type: application/json" \
     -d '{"Players": "24/32", "Map": "de_dust2"}' \
     http://localhost:5000/server/1/info
```
