# Game Server Monitor

A monitoring application for tracking game server status and availability.

## Features

- Register game servers for monitoring
- Automatic server polling and status updates
- Server details and information display
- API for batch server imports
- Webhook logging for notifications

## Usage

Access the web interface at http://localhost:8080

### Register a Server

1. Navigate to "Register Server"
2. Enter the server type, address, and ports
3. Submit to test and register the server

### API Endpoints

- `GET /` - Server list
- `GET /panel/view?s=<id>` - Server details
- `POST /api/servers/import` - Import server data via JSON
- `GET /api/webhook` - View webhook logs
- `POST /api/webhook` - Receive webhook callbacks
