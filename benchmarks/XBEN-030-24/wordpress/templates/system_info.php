<div class="card">
    <div class="card-header">
        <h2>System Information</h2>
    </div>
    <div class="card-body">
        <table class="data-table">
            <tr>
                <td><strong>Hostname</strong></td>
                <td><?php echo htmlspecialchars($hostname); ?></td>
            </tr>
            <tr>
                <td><strong>Uptime</strong></td>
                <td><?php echo htmlspecialchars(trim($uptime)); ?></td>
            </tr>
            <tr>
                <td><strong>Memory Total</strong></td>
                <td><?php echo getHumanReadableDatasize($memTotal); ?></td>
            </tr>
            <tr>
                <td><strong>Memory Available</strong></td>
                <td><?php echo getHumanReadableDatasize($memAvail); ?></td>
            </tr>
            <tr>
                <td><strong>Memory Used</strong></td>
                <td><?php echo $memUsedPct; ?>%</td>
            </tr>
        </table>
    </div>
</div>
