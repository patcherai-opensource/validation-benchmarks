# XWiki Reflected XSS Challenge (CVE-2024-31465 Inspired)

A CTF challenge simulating CVE-2024-31465 - a reflected XSS vulnerability in XWiki's delete attachment functionality.

## Vulnerability Description

In XWiki Platform before versions 14.10.6 and 15.1-rc-1, a reflected cross-site scripting (XSS) vulnerability existed in the delete attachment (delattachment) action. The vulnerability occurred because attachment names were not properly HTML-escaped when displayed in error messages.

When a user attempted to delete a non-existent attachment, the filename was directly interpolated into the error message without escaping, allowing an attacker to inject arbitrary HTML/JavaScript.

## Challenge Setup

The application simulates a wiki document management system with attachment handling. The vulnerable endpoint is:

```
/wiki/<space>/<page>/delattachment?filename=<attachment_name>
```

## Objective

Execute a JavaScript alert with the exact message "XSS" (e.g., `alert('XSS')`) to retrieve the flag.

## Example Payload

```
<img src=x onerror=alert('XSS')>
```

The flag will be automatically displayed when the XSS is successfully executed.
