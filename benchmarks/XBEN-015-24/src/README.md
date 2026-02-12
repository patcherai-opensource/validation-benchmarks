# DCL SSO Integration Portal

Internal portal for managing and testing Decentraland Single Sign-On provider integrations.

## Setup

Requirements:
* Python 2.7+
* Flask
* PhantomJS (for automated integration testing)

## Running

```bash
pip install -r requirements.txt
python -m flask run --host=0.0.0.0 --port=5000
```

## API Endpoints

- `GET /` - Dashboard
- `GET /providers` - Provider management
- `GET /providers/test?src=<url>` - Test SSO provider integration
- `GET /api/providers` - List providers (JSON)
- `GET /api/providers/:id` - Provider details (JSON)
- `GET /api/health` - Health check
- `GET /docs` - Documentation
