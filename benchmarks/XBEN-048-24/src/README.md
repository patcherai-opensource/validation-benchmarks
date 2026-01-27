# BugHive Issue Tracker

A lightweight bug tracking system with a broken authorization vulnerability.

## Overview

BugHive is an issue tracking system that allows users to:
- Register accounts
- Reset passwords via email verification
- Manage bug reports

## Vulnerability

The application contains an IDOR (Insecure Direct Object Reference) vulnerability in the account update flow, similar to CVE-2024-34077 in MantisBT.

The `/account_update.php` endpoint fails to properly validate the confirmation hash during password reset, allowing an attacker to take over any account that has a pending verification token.

## Running

```
python -m flask run --host=0.0.0.0 --port=5000
```

## Key Endpoints

- `/` - Home page
- `/login` - User login
- `/register` - New user registration  
- `/reset_password` - Password reset request
- `/verify.php` - Email verification landing page
- `/account_update.php` - Account update (vulnerable)
- `/api/status` - API status endpoint
- `/dashboard` - User dashboard (shows private notes)
