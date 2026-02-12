<h1 class="h3 mb-4 text-gray-800">Dashboard</h1>

<div class="row">
    <div class="col-xl-3 col-md-6 mb-4">
        <div class="card border-left-primary shadow h-100 py-2">
            <div class="card-body">
                <div class="row no-gutters align-items-center">
                    <div class="col mr-2">
                        <div class="text-xs font-weight-bold text-primary text-uppercase mb-1">Hostname</div>
                        <div class="h5 mb-0 font-weight-bold text-gray-800"><?php echo htmlspecialchars($systemInfo['hostname']); ?></div>
                    </div>
                    <div class="col-auto">
                        <i class="fas fa-server fa-2x text-gray-300"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="col-xl-3 col-md-6 mb-4">
        <div class="card border-left-success shadow h-100 py-2">
            <div class="card-body">
                <div class="row no-gutters align-items-center">
                    <div class="col mr-2">
                        <div class="text-xs font-weight-bold text-success text-uppercase mb-1">Kernel</div>
                        <div class="h5 mb-0 font-weight-bold text-gray-800"><?php echo htmlspecialchars($systemInfo['kernel']); ?></div>
                    </div>
                    <div class="col-auto">
                        <i class="fas fa-microchip fa-2x text-gray-300"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="col-xl-3 col-md-6 mb-4">
        <div class="card border-left-info shadow h-100 py-2">
            <div class="card-body">
                <div class="row no-gutters align-items-center">
                    <div class="col mr-2">
                        <div class="text-xs font-weight-bold text-info text-uppercase mb-1">PHP Version</div>
                        <div class="h5 mb-0 font-weight-bold text-gray-800"><?php echo htmlspecialchars($systemInfo['php_version']); ?></div>
                    </div>
                    <div class="col-auto">
                        <i class="fas fa-code fa-2x text-gray-300"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="col-xl-3 col-md-6 mb-4">
        <div class="card border-left-warning shadow h-100 py-2">
            <div class="card-body">
                <div class="row no-gutters align-items-center">
                    <div class="col mr-2">
                        <div class="text-xs font-weight-bold text-warning text-uppercase mb-1">RaspAP Version</div>
                        <div class="h5 mb-0 font-weight-bold text-gray-800"><?php echo RASPI_VERSION; ?></div>
                    </div>
                    <div class="col-auto">
                        <i class="fas fa-wifi fa-2x text-gray-300"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-lg-6">
        <div class="card shadow mb-4">
            <div class="card-header py-3">
                <h6 class="m-0 font-weight-bold text-primary">Network Interfaces</h6>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-bordered" width="100%" cellspacing="0">
                        <thead><tr><th>Interface</th><th>Status</th></tr></thead>
                        <tbody>
                        <?php
                        $interfaces = getNetworkInterfaces();
                        foreach ($interfaces as $iface): ?>
                            <tr>
                                <td><?php echo htmlspecialchars($iface); ?></td>
                                <td><span class="badge badge-success">UP</span></td>
                            </tr>
                        <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
    <div class="col-lg-6">
        <div class="card shadow mb-4">
            <div class="card-header py-3">
                <h6 class="m-0 font-weight-bold text-primary">WireGuard Status</h6>
            </div>
            <div class="card-body">
                <?php $wgStatus = getWireguardStatus(); ?>
                <?php if ($wgStatus['active']): ?>
                    <span class="badge badge-success">Active</span>
                    <pre class="mt-2 small"><?php echo htmlspecialchars($wgStatus['output']); ?></pre>
                <?php else: ?>
                    <span class="badge badge-secondary">Inactive</span>
                    <p class="mt-2 text-muted">WireGuard is not currently active. Configure it from the <a href="/?page=wg_conf">WireGuard</a> page.</p>
                <?php endif; ?>
            </div>
        </div>
    </div>
</div>
