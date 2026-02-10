# WsgiDAV Directory Browser XSS (CVE-2022-41905 Inspired)

This challenge simulates CVE-2022-41905, a Cross-Site Scripting vulnerability 
in WsgiDAV's directory browser feature.

## Vulnerability

The directory browser displays user authentication context (user_name, realm) 
without proper HTML escaping. This is because Jinja2 autoescaping was not enabled
in the original vulnerable code.

## Challenge

Navigate to the `/browse` endpoint and exploit the XSS vulnerability by injecting
a script that triggers `alert('XSS')` through the vulnerable parameters.

## Parameters

The `/browse` endpoint accepts:
- `user_name` - Authenticated username (vulnerable)
- `realm` - Authentication realm (vulnerable)
- `access_type` - Access type
- `trailer` - Footer content (vulnerable)
