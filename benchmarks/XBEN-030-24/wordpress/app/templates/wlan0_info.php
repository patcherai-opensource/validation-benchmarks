<h1 class="h3 mb-4 text-gray-800"><i class="fas fa-network-wired mr-2"></i>WiFi Client</h1>

<div class="row">
    <div class="col-lg-12">
        <div class="card shadow mb-4">
            <div class="card-header py-3">
                <h6 class="m-0 font-weight-bold text-primary">Interface Information</h6>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-bordered">
                        <tr><td><strong>Interface</strong></td><td><?php echo RASPI_WIFI_AP_INTERFACE; ?></td></tr>
                        <tr><td><strong>Status</strong></td><td><span class="badge badge-secondary">Not configured</span></td></tr>
                        <tr><td><strong>IP Address</strong></td><td>-</td></tr>
                        <tr><td><strong>Subnet Mask</strong></td><td>-</td></tr>
                        <tr><td><strong>MAC Address</strong></td><td>-</td></tr>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-lg-12">
        <div class="card shadow mb-4">
            <div class="card-header py-3">
                <h6 class="m-0 font-weight-bold text-primary">Available Networks</h6>
            </div>
            <div class="card-body">
                <p class="text-muted">No wireless networks detected. The WiFi adapter may not be available.</p>
            </div>
        </div>
    </div>
</div>
