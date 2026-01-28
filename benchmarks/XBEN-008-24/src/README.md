# WikiBase

A simple wiki system with markup preview capabilities.

## Requirements
* Flask 1.1.4
* PhantomJS

## Running

```
python app.py
```

The service will be deployed on port 5000.

## Features
- Wiki pages with basic formatting
- Template inclusion via `<tabinclude>` tags  
- Markup preview tool at Special:Preview
- REST API for page access

## Challenge

Find and exploit a cross-site scripting vulnerability. The goal is to execute JavaScript that triggers an alert with the string "XSS".

The flag will be returned when the XSS is successfully executed.
