# DataVault Analytics - Installation Guide

## Prerequisites

- Python 3.8+
- MySQL 5.7+ or PostgreSQL 12+
- Minimum 4GB RAM

## Quick Start

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Configure the database connection in your environment or configuration file:
   ```
   export DATABASE_URI="mysql+pymysql://user:pass@host/dbname"
   ```

3. Initialize the database:
   ```
   python manage.py init-db
   ```

4. Create an admin user:
   ```
   python manage.py create-admin
   ```

5. Start the application:
   ```
   python run.py
   ```

## Configuration

### Security Settings

The platform uses a signing key for session management and token generation.
The default key is set in `defaults.py`:

```python
PLATFORM_SIGNING_KEY = "REPLACE_WITH_YOUR_OWN_RANDOM_KEY"
```

**Important:** You must override this value in production by setting the
`SIGNING_KEY` environment variable:

```
export SIGNING_KEY="your-secure-random-key-here"
```

Use a tool like `openssl rand -base64 42` to generate a strong random key.

### Session Options

| Setting | Default | Description |
|---------|---------|-------------|
| SESSION_COOKIE_HTTPONLY | True | Prevent JS access to cookies |
| SESSION_COOKIE_SAMESITE | Lax | SameSite cookie attribute |
| SESSION_LIFETIME_HOURS | 8 | Session timeout in hours |

### User Roles

| Role | Description |
|------|-------------|
| admin | Full access to all features including platform settings |
| editor | Can create and modify dashboards and charts |
| viewer | Read-only access to published dashboards |

## Troubleshooting

If you encounter session-related issues, verify that the `SIGNING_KEY`
environment variable is properly set and consistent across all application
instances.

## Support

For issues and feature requests, contact your system administrator.
