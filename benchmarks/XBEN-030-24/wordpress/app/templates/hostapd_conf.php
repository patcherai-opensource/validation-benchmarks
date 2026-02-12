<h1 class="h3 mb-4 text-gray-800"><i class="fas fa-broadcast-tower mr-2"></i>Hotspot Configuration</h1>

<div class="row">
    <div class="col-lg-12">
        <div class="card shadow mb-4">
            <div class="card-header py-3">
                <h6 class="m-0 font-weight-bold text-primary">Basic Settings</h6>
            </div>
            <div class="card-body">
                <form>
                    <input type="hidden" name="csrf_token" value="<?php echo htmlspecialchars($csrf_token); ?>">
                    <div class="form-group">
                        <label for="ssid">SSID</label>
                        <input type="text" class="form-control" id="ssid" value="raspi-webgui" readonly>
                    </div>
                    <div class="form-group">
                        <label for="wpa_passphrase">WPA Passphrase</label>
                        <input type="password" class="form-control" id="wpa_passphrase" value="ChangeMe" readonly>
                    </div>
                    <div class="form-group">
                        <label for="channel">Channel</label>
                        <select class="form-control" id="channel" disabled>
                            <option value="1">1</option>
                            <option value="6" selected>6</option>
                            <option value="11">11</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="country_code">Country Code</label>
                        <input type="text" class="form-control" id="country_code" value="US" readonly>
                    </div>
                    <button type="button" class="btn btn-secondary" disabled>Save settings</button>
                    <small class="form-text text-muted">Hotspot configuration is read-only in this environment.</small>
                </form>
            </div>
        </div>
    </div>
</div>
