<h1 class="h3 mb-4 text-gray-800"><i class="fas fa-key mr-2"></i>WireGuard</h1>

<div class="row">
    <div class="col-lg-12">
        <div class="card shadow mb-4">
            <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                <h6 class="m-0 font-weight-bold text-primary">WireGuard Configuration</h6>
            </div>
            <div class="card-body">
                <form id="wg-config-form">
                    <input type="hidden" name="csrf_token" value="<?php echo htmlspecialchars($csrf_token); ?>">
                    <div class="form-group">
                        <label for="wg-interface">Interface</label>
                        <select class="form-control" id="wg-interface" name="interface">
                            <option value="wg0">wg0</option>
                            <option value="wg1">wg1</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="wg-address">Address</label>
                        <input type="text" class="form-control" id="wg-address" name="address" value="10.10.10.1/24" placeholder="10.10.10.1/24">
                    </div>
                    <div class="form-group">
                        <label for="wg-port">Listen Port</label>
                        <input type="number" class="form-control" id="wg-port" name="port" value="<?php echo RASPI_WG_PORT; ?>">
                    </div>
                    <div class="form-group">
                        <label for="wg-dns">DNS</label>
                        <input type="text" class="form-control" id="wg-dns" name="dns" value="1.1.1.1" placeholder="1.1.1.1">
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-lg-12">
        <div class="card shadow mb-4">
            <div class="card-header py-3">
                <h6 class="m-0 font-weight-bold text-primary">Key Generation</h6>
            </div>
            <div class="card-body">
                <p class="mb-3">Generate WireGuard keypairs for server and peer configurations.</p>
                <form id="wg-keygen-form">
                    <input type="hidden" name="csrf_token" value="<?php echo htmlspecialchars($csrf_token); ?>">
                    <div class="form-group">
                        <label for="wg-entity">Configuration Name</label>
                        <input type="text" class="form-control" id="wg-entity" name="entity" placeholder="e.g. server, peer1, peer2" required>
                        <small class="form-text text-muted">Enter a name for this WireGuard configuration entity.</small>
                    </div>
                    <button type="submit" class="btn btn-primary" id="btn-genkey">
                        <i class="fas fa-key mr-1"></i> Generate Keys
                    </button>
                </form>
                <div id="keygen-result" class="mt-3" style="display:none;">
                    <div class="alert alert-success">
                        <strong>Keys generated successfully!</strong>
                    </div>
                    <div class="form-group">
                        <label>Public Key</label>
                        <input type="text" class="form-control" id="wg-pubkey" readonly>
                    </div>
                    <div class="form-group">
                        <label>Private Key</label>
                        <input type="text" class="form-control" id="wg-privkey" readonly>
                    </div>
                </div>
                <div id="keygen-error" class="mt-3" style="display:none;">
                    <div class="alert alert-danger" id="keygen-error-msg"></div>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-lg-12">
        <div class="card shadow mb-4">
            <div class="card-header py-3">
                <h6 class="m-0 font-weight-bold text-primary">Peers</h6>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-bordered" id="peersTable" width="100%" cellspacing="0">
                        <thead>
                            <tr>
                                <th>Peer</th>
                                <th>Public Key</th>
                                <th>Allowed IPs</th>
                                <th>Latest Handshake</th>
                                <th>Transfer</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td colspan="5" class="text-center text-muted">No peers configured</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
$(document).ready(function() {
    $('#wg-keygen-form').on('submit', function(e) {
        e.preventDefault();
        var entity = $('#wg-entity').val();
        var csrf = $('input[name="csrf_token"]', this).val();

        $('#keygen-result').hide();
        $('#keygen-error').hide();
        $('#btn-genkey').prop('disabled', true).html('<i class="fas fa-spinner fa-spin mr-1"></i> Generating...');

        $.ajax({
            url: '/ajax/networking/get_wgkey.php',
            method: 'POST',
            data: {
                entity: entity,
                csrf_token: csrf
            },
            dataType: 'json',
            success: function(response) {
                if (response.return === 0) {
                    $('#wg-pubkey').val(response.pubkey);
                    $('#wg-privkey').val(response.privkey);
                    $('#keygen-result').show();
                } else {
                    $('#keygen-error-msg').text(response.output || 'Key generation failed');
                    $('#keygen-error').show();
                }
            },
            error: function(xhr) {
                var msg = 'Request failed';
                try {
                    var resp = JSON.parse(xhr.responseText);
                    msg = resp.error || msg;
                } catch(e) {}
                $('#keygen-error-msg').text(msg);
                $('#keygen-error').show();
            },
            complete: function() {
                $('#btn-genkey').prop('disabled', false).html('<i class="fas fa-key mr-1"></i> Generate Keys');
            }
        });
    });
});
</script>
