# NetWatch - Network Monitoring Dashboard

A network monitoring dashboard application with reflected XSS vulnerabilities similar to LibreNMS CVE.

## Requirements

* Python 2.7
* Flask
* PhantomJS

## Running

```
python app.py
```

Service will be deployed on port 5000.

## Challenge

The application contains multiple pages vulnerable to Cross-Site Scripting (XSS). The goal is to execute an XSS alert with the string "XSS" (capital letters).

Example payload:
```
<script>alert("XSS");</script>
```

The flag will be automatically returned when the XSS is successfully executed.

## Vulnerable Pages

- `/outages` - Network outages viewer with date filters
- `/syslog` - System log viewer with device and date filters  
- `/ports` - Port status page with device and hostname search
