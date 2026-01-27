# GameTracker - Game Server Browser

A web application for tracking and browsing game servers.

## Features

- Register game servers via REST API
- Browse registered servers
- View detailed server information
- Support for custom server metadata fields

## API Endpoints

- `GET /` - Home page
- `GET /servers` - Browse all registered servers
- `GET /api/servers` - List servers (JSON)
- `POST /api/servers` - Register a new server
- `GET /server/<id>` - View server details

## Running

```bash
python -m flask run --host=0.0.0.0 --port=5000
```

## Server Registration

Send a POST request to `/api/servers` with JSON body:

```json
{
    "name": "My Server",
    "ip": "192.168.1.100",
    "port": 27015,
    "game": "Counter-Strike",
    "map": "de_dust2",
    "players": 12,
    "maxplayers": 32,
    "extra": {
        "Region": "US East",
        "Custom Field": "Custom Value"
    }
}
```
