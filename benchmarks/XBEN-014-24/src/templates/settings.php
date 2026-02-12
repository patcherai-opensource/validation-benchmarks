    <div class="container">
        <div class="card">
            <h2>Account Settings</h2>
            <div class="form-group">
                <label>Username</label>
                <input type="text" value="<?php echo htmlspecialchars($_SESSION['user_id']); ?>" disabled>
            </div>
            <div class="form-group">
                <label>Display Name</label>
                <input type="text" value="<?php echo htmlspecialchars($_SESSION['display_name']); ?>" disabled>
            </div>
            <div class="form-group">
                <label>Role</label>
                <input type="text" value="<?php echo htmlspecialchars($_SESSION['role']); ?>" disabled>
            </div>
        </div>
        <div class="card">
            <h2>Security</h2>
            <p style="color: #666; font-size: 14px; margin-bottom: 16px;">
                Two-factor authentication is managed by your system administrator. Contact IT support to update your TOTP configuration.
            </p>
            <table class="data-table">
                <tr>
                    <td>Two-Factor Authentication</td>
                    <td><span class="badge badge-success">Enabled</span></td>
                </tr>
                <tr>
                    <td>Last Password Change</td>
                    <td><?php echo date('Y-m-d', strtotime('-45 days')); ?></td>
                </tr>
                <tr>
                    <td>Session Timeout</td>
                    <td>30 minutes</td>
                </tr>
            </table>
        </div>
    </div>