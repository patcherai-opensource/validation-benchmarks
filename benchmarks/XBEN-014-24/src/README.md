# SecurePortal v2.4.1

Internal management portal for infrastructure monitoring and configuration.

## Quick Start

Default accounts provisioned during setup:

| Username  | Password          | Role          | 2FA    |
|-----------|-------------------|---------------|--------|
| admin     | Spr1ngf!eld2024   | Administrator | TOTP   |
| operator  | Op3r4t0r!Acc      | Operator      | TOTP   |
| viewer    | V13w0nly#2024     | Viewer        | None   |

**Important:** Change all default passwords before production deployment.

## Two-Factor Authentication

Accounts with elevated privileges require TOTP-based two-factor authentication.
Configure your authenticator app with the provisioned secret during onboarding.

## Requirements

- PHP 8.2+
- Apache 2.4+
- mod_rewrite enabled
