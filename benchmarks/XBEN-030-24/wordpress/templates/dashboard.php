<div class="card">
    <div class="card-header">
        <h2>System Dashboard</h2>
    </div>
    <div class="card-body">
        <div class="stat-grid">
            <div class="stat-item">
                <div class="stat-label">Hostname</div>
                <div class="stat-value"><?php echo htmlspecialchars($hostname); ?></div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Uptime</div>
                <div class="stat-value"><?php echo htmlspecialchars(trim($uptime)); ?></div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Memory Usage</div>
                <div class="stat-value"><?php echo $memUsedPct; ?>%</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Total Memory</div>
                <div class="stat-value"><?php echo getHumanReadableDatasize($memTotal); ?></div>
            </div>
        </div>
    </div>
</div>

<div class="card">
    <div class="card-header">
        <h3>Network Interfaces</h3>
    </div>
    <div class="card-body">
        <table class="data-table">
            <thead>
                <tr>
                    <th>Interface</th>
                    <th>Status</th>
                    <th>Type</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>eth0</td>
                    <td><span class="status-active">UP</span></td>
                    <td>Ethernet</td>
                </tr>
                <tr>
                    <td>wlan0</td>
                    <td><span class="status-inactive">DOWN</span></td>
                    <td>Wireless</td>
                </tr>
            </tbody>
        </table>
    </div>
</div>
