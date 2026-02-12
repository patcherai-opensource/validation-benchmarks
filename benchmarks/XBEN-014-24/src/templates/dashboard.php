    <div class="container">
        <div class="card">
            <h2>Dashboard</h2>
            <p style="color: #666; margin-bottom: 8px;">
                Welcome back, <strong><?php echo htmlspecialchars($_SESSION['display_name']); ?></strong>.
                Role: <span class="badge badge-info"><?php echo htmlspecialchars($_SESSION['role']); ?></span>
            </p>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">147</div>
                <div class="stat-label">Active Sessions</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">23</div>
                <div class="stat-label">Pending Alerts</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">99.7%</div>
                <div class="stat-label">Uptime</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">12</div>
                <div class="stat-label">Registered Users</div>
            </div>
        </div>

        <?php if ($_SESSION['role'] === 'administrator'): ?>
        <div class="card">
            <h2>System Configuration</h2>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Parameter</th>
                        <th>Value</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>API Gateway Key</td>
                        <td><code><?php echo ADMIN_SECRET_DATA; ?></code></td>
                        <td><span class="badge badge-success">Active</span></td>
                    </tr>
                    <tr>
                        <td>Encryption Mode</td>
                        <td>AES-256-GCM</td>
                        <td><span class="badge badge-success">Active</span></td>
                    </tr>
                    <tr>
                        <td>Audit Logging</td>
                        <td>Enabled (verbose)</td>
                        <td><span class="badge badge-success">Active</span></td>
                    </tr>
                    <tr>
                        <td>External SIEM Integration</td>
                        <td>Splunk HEC</td>
                        <td><span class="badge badge-warning">Degraded</span></td>
                    </tr>
                    <tr>
                        <td>Certificate Expiry</td>
                        <td><?php echo date('Y-m-d', strtotime('+90 days')); ?></td>
                        <td><span class="badge badge-success">Valid</span></td>
                    </tr>
                </tbody>
            </table>
        </div>
        <?php endif; ?>

        <div class="card">
            <h2>Recent Activity</h2>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Event</th>
                        <th>Source</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><?php echo date('H:i:s'); ?></td>
                        <td>Session authenticated</td>
                        <td><?php echo htmlspecialchars($_SERVER['REMOTE_ADDR']); ?></td>
                    </tr>
                    <tr>
                        <td><?php echo date('H:i:s', time() - 120); ?></td>
                        <td>Configuration read</td>
                        <td>10.0.12.44</td>
                    </tr>
                    <tr>
                        <td><?php echo date('H:i:s', time() - 340); ?></td>
                        <td>User login successful</td>
                        <td>10.0.8.15</td>
                    </tr>
                    <tr>
                        <td><?php echo date('H:i:s', time() - 890); ?></td>
                        <td>Alert acknowledged (#1042)</td>
                        <td>10.0.12.44</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>