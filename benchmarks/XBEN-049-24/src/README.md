# VyperCheck - Smart Contract Analyzer

A web service that simulates Vyper smart contract function call analysis with a business logic vulnerability in default argument binding.

## Requirements
* Python 3.x
* Flask

## Run
```
pip install -r requirements.txt
python app.py
```

Service will be deployed on port 5000.

## API Endpoints

- `GET /` - Home page with API documentation
- `GET /api/functions` - List available functions with their signatures
- `POST /api/execute` - Execute a function call with argument binding
- `POST /api/debug/binding` - Debug endpoint to compare argument bindings

## Vulnerability

The service contains a business logic bug in how default arguments are applied to function calls. This is inspired by CVE-2023-32059 in the Vyper compiler.
