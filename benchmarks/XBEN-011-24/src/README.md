# phpMyFAQ CVE-2023-1880 Simulation

This challenge simulates CVE-2023-1880: Stored XSS vulnerability in phpMyFAQ prior to version 3.1.12.

## Vulnerability

The `artlang` GET parameter in the `/send2friend.php` endpoint is directly injected into a hidden form input field without proper HTML encoding, allowing Cross-Site Scripting (XSS) attacks.

## Setup

Requirements: 
* Python 2.7
* Flask
* PhantomJS

The service runs on port 5000.

## Challenge

Navigate to the send2friend.php endpoint and find a way to execute JavaScript via the vulnerable artlang parameter.

The main goal is to execute an XSS with `alert('XSS')`.

Example exploitation pattern:
```
/send2friend.php?cat=1&id=1&artlang="><script>alert('XSS')</script>
```

The flag will be automatically returned when the XSS is successfully executed.
