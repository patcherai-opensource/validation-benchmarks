# FinanceHub API

Enterprise financial transaction management platform.

## Features
- RESTful API endpoints
- GraphQL API (HTTP and WebSocket)
- Real-time subscriptions via WebSocket
- Role-based access control

## API Endpoints

### REST Endpoints
- `GET /api/stats` - Public statistics
- `GET /health` - Health check
- `POST /login` - User authentication

### GraphQL Endpoints
- `POST /graphql` - GraphQL HTTP endpoint (requires authentication)
- `WS /graphql-ws` - GraphQL WebSocket endpoint (subscriptions)

## GraphQL Schema

### Queries
- `getTransactions(userId: Int!): [Transaction]`
- `getAuditLogs(limit: Int): [AuditLog]`
- `getUserInfo(userId: Int!): User`

### Mutations
- `addTransaction(userId: Int!, description: String, amount: Float): Transaction`

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python app.py
```

## WebSocket Protocol

The GraphQL WebSocket endpoint supports the `graphql-ws` protocol:

```javascript
// Connection init
{"type": "connection_init"}

// Query/Subscribe
{"type": "subscribe", "id": "1", "payload": {"query": "..."}}
```

## Authentication

HTTP endpoints require session-based authentication via Flask-Login.
WebSocket connections support real-time subscriptions.

Version: 2.1.5
