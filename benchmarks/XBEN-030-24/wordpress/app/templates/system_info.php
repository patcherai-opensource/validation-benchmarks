<h1 class="h3 mb-4 text-gray-800"><i class="fas fa-info-circle mr-2"></i>System Information</h1>

<div class="row">
    <div class="col-lg-12">
        <div class="card shadow mb-4">
            <div class="card-header py-3">
                <h6 class="m-0 font-weight-bold text-primary">System</h6>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-bordered">
                        <tr><td width="200"><strong>Hostname</strong></td><td><?php echo htmlspecialchars($systemInfo['hostname']); ?></td></tr>
                        <tr><td><strong>Kernel</strong></td><td><?php echo htmlspecialchars($systemInfo['kernel']); ?></td></tr>
                        <tr><td><strong>PHP Version</strong></td><td><?php echo htmlspecialchars($systemInfo['php_version']); ?></td></tr>
                        <tr><td><strong>Web Server</strong></td><td>Apache/2.4</td></tr>
                        <tr><td><strong>RaspAP Version</strong></td><td><?php echo RASPI_VERSION; ?></td></tr>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-lg-6">
        <div class="card shadow mb-4">
            <div class="card-header py-3">
                <h6 class="m-0 font-weight-bold text-primary">Memory Usage</h6>
            </div>
            <div class="card-body">
                <?php
                $meminfo = @file_get_contents('/proc/meminfo');
                $memtotal = 0;
                $memfree = 0;
                if ($meminfo) {
                    preg_match('/MemTotal:\s+(\d+)/', $meminfo, $m);
                    $memtotal = isset($m[1]) ? intval($m[1]) : 0;
                    preg_match('/MemAvailable:\s+(\d+)/', $meminfo, $m);
                    $memfree = isset($m[1]) ? intval($m[1]) : 0;
                }
                $memused = $memtotal - $memfree;
                $pct = $memtotal > 0 ? round(($memused / $memtotal) * 100) : 0;
                ?>
                <div class="mb-1">
                    <span>Used: <?php echo round($memused / 1024); ?> MB / <?php echo round($memtotal / 1024); ?> MB</span>
                    <span class="float-right"><?php echo $pct; ?>%</span>
                </div>
                <div class="progress">
                    <div class="progress-bar bg-info" role="progressbar" style="width: <?php echo $pct; ?>%"></div>
                </div>
            </div>
        </div>
    </div>
    <div class="col-lg-6">
        <div class="card shadow mb-4">
            <div class="card-header py-3">
                <h6 class="m-0 font-weight-bold text-primary">Disk Usage</h6>
            </div>
            <div class="card-body">
                <?php
                $diskTotal = disk_total_space('/');
                $diskFree = disk_free_space('/');
                $diskUsed = $diskTotal - $diskFree;
                $diskPct = $diskTotal > 0 ? round(($diskUsed / $diskTotal) * 100) : 0;
                ?>
                <div class="mb-1">
                    <span>Used: <?php echo round($diskUsed / 1073741824, 1); ?> GB / <?php echo round($diskTotal / 1073741824, 1); ?> GB</span>
                    <span class="float-right"><?php echo $diskPct; ?>%</span>
                </div>
                <div class="progress">
                    <div class="progress-bar bg-warning" role="progressbar" style="width: <?php echo $diskPct; ?>%"></div>
                </div>
            </div>
        </div>
    </div>
</div>
