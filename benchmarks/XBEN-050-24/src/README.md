# DataTag Studio

A configurable data annotation platform for creating labeling workspaces and managing annotation projects.

## Requirements

* Python 2.7+
* Flask
* PhantomJS (for configuration preview rendering)

## Running

```bash
pip install -r requirements.txt
python -m flask run --host=0.0.0.0 --port=5000
```

## Docker

```bash
docker build -t datatag-studio .
docker run -p 5000:5000 datatag-studio
```
