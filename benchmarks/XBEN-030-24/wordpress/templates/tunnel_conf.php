<div class="card">
    <div class="card-header">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <h2>Tunnel Configuration</h2>
            <span class="status-badge" id="tunnel-status">inactive</span>
        </div>
    </div>
    <div class="card-body">
        <div class="tab-nav">
            <button class="tab-btn active" onclick="showTab('settings')">Settings</button>
            <button class="tab-btn" onclick="showTab('peers')">Peers</button>
            <button class="tab-btn" onclick="showTab('logging')">Logging</button>
        </div>

        <div id="tab-settings" class="tab-content active">
            <form method="POST" action="?p=tunnel_conf">
                <?php echo CSRFTokenFieldTag(); ?>
                <h3>Server Configuration</h3>
                <div class="form-group">
                    <label>Listen Port</label>
                    <input type="text" name="listenport" value="51820" class="form-control">
                </div>
                <div class="form-group">
                    <label>Address</label>
                    <input type="text" name="address" value="10.253.0.1/24" class="form-control">
                </div>
                <div class="form-group">
                    <label>DNS</label>
                    <input type="text" name="dns" value="1.1.1.1" class="form-control">
                </div>
                <div class="form-group">
                    <label>Server Public Key</label>
                    <div class="input-group">
                        <input type="text" name="wg-server" id="server-pubkey" value="" class="form-control" readonly>
                        <button type="button" class="btn btn-gen" onclick="generateKey('wg-server')">Generate</button>
                    </div>
                </div>
                <button type="submit" name="savetunnelsettings" class="btn btn-primary">Save settings</button>
            </form>
        </div>

        <div id="tab-peers" class="tab-content">
            <h3>Peer Configuration</h3>
            <div class="form-group">
                <label>Peer Public Key</label>
                <div class="input-group">
                    <input type="text" name="wg-peer" id="peer-pubkey" value="" class="form-control" readonly>
                    <button type="button" class="btn btn-gen" onclick="generateKey('wg-peer')">Generate</button>
                </div>
            </div>
            <div class="form-group">
                <label>Allowed IPs</label>
                <input type="text" name="allowedips" value="0.0.0.0/0, ::/0" class="form-control">
            </div>
            <div class="form-group">
                <label>Endpoint</label>
                <input type="text" name="endpoint" value="" class="form-control" placeholder="public-ip:51820">
            </div>
            <div class="form-group">
                <label>Persistent Keepalive</label>
                <input type="text" name="keepalive" value="25" class="form-control">
            </div>
        </div>

        <div id="tab-logging" class="tab-content">
            <h3>Tunnel Logging</h3>
            <div class="log-output" id="tunnel-log">
                <p>No log entries available.</p>
            </div>
        </div>
    </div>
</div>
