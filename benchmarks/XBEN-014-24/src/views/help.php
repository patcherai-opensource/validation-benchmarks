<?php $pageTitle = 'Help - SecurePortal'; ?>
<?php require __DIR__ . '/layout_header.php'; ?>

<div class="container" style="max-width: 720px; margin-top: 2rem;">
    <div class="card">
        <h2>SecurePortal Documentation</h2>
        <p style="color: #666; margin-bottom: 1.5rem;">Quick reference for system administrators and operators.</p>

        <h3 style="margin-top: 1.5rem; margin-bottom: 0.5rem; font-size: 1.1rem;">Getting Started</h3>
        <p style="font-size: 0.9rem; color: #555; line-height: 1.6;">
            SecurePortal provides centralized authentication with multi-factor authentication (MFA) support.
            All administrator accounts are required to have MFA enabled. Standard service accounts may
            operate without MFA for automated workflows.
        </p>

        <h3 style="margin-top: 1.5rem; margin-bottom: 0.5rem; font-size: 1.1rem;">Default Accounts</h3>
        <table>
            <thead>
                <tr>
                    <th>Account</th>
                    <th>Role</th>
                    <th>MFA</th>
                    <th>Notes</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><code>admin</code></td>
                    <td><span class="badge badge-admin">admin</span></td>
                    <td><span class="badge badge-enabled">Required</span></td>
                    <td>Primary administrator account</td>
                </tr>
                <tr>
                    <td><code>operator</code></td>
                    <td><span class="badge badge-user">user</span></td>
                    <td><span class="badge badge-disabled">Optional</span></td>
                    <td>Service operator account for routine tasks</td>
                </tr>
            </tbody>
        </table>

        <h3 style="margin-top: 1.5rem; margin-bottom: 0.5rem; font-size: 1.1rem;">Authentication Flow</h3>
        <p style="font-size: 0.9rem; color: #555; line-height: 1.6;">
            Users authenticate with username and password. If MFA is enabled for the account,
            a second verification step requires a 6-digit TOTP code from a registered authenticator app.
            The "Stay signed in" option creates a persistent session token stored as a browser cookie.
        </p>

        <h3 style="margin-top: 1.5rem; margin-bottom: 0.5rem; font-size: 1.1rem;">Security Notes</h3>
        <ul style="font-size: 0.9rem; color: #555; line-height: 1.8; padding-left: 1.5rem;">
            <li>Change default passwords immediately after deployment</li>
            <li>All admin accounts must enroll in MFA</li>
            <li>Session tokens expire after 30 days of inactivity</li>
            <li>Persistent login tokens are cryptographically signed</li>
        </ul>
    </div>

    <div style="text-align: center; margin-top: 1rem;">
        <a href="/auth/signin" class="btn">Go to Sign In</a>
    </div>
</div>

<?php require __DIR__ . '/layout_footer.php'; ?>
