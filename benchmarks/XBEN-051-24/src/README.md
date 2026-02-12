# Label Studio

Open source data labeling platform for machine learning.

## Quick Start

```
pip install -r requirements.txt
python -m flask run --host=0.0.0.0 --port=5000
```

## API Endpoints

- `GET /projects/` - List projects
- `GET /projects/<id>/` - Project details
- `POST /projects/create/` - Create new project
- `POST /projects/upload-example/` - Generate example task from config
- `POST /projects/validate-config/` - Validate label configuration
- `GET /api/projects/` - List projects (JSON API)
- `GET /api/projects/<id>/` - Project details (JSON API)
