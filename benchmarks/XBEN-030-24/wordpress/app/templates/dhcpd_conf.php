<h1 class="h3 mb-4 text-gray-800"><i class="fas fa-network-wired mr-2"></i>DHCP Server</h1>

<div class="row">
    <div class="col-lg-12">
        <div class="card shadow mb-4">
            <div class="card-header py-3">
                <h6 class="m-0 font-weight-bold text-primary">DHCP Configuration</h6>
            </div>
            <div class="card-body">
                <form>
                    <input type="hidden" name="csrf_token" value="<?php echo htmlspecialchars($csrf_token); ?>">
                    <div class="form-group">
                        <label for="dhcp-range-start">Range Start</label>
                        <input type="text" class="form-control" id="dhcp-range-start" value="192.168.50.50" readonly>
                    </div>
                    <div class="form-group">
                        <label for="dhcp-range-end">Range End</label>
                        <input type="text" class="form-control" id="dhcp-range-end" value="192.168.50.150" readonly>
                    </div>
                    <div class="form-group">
                        <label for="dhcp-lease">Lease Time</label>
                        <input type="text" class="form-control" id="dhcp-lease" value="12h" readonly>
                    </div>
                    <button type="button" class="btn btn-secondary" disabled>Save settings</button>
                </form>
            </div>
        </div>
    </div>
</div>
