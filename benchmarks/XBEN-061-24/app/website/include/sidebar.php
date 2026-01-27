<div class="col-md-4">
    <!-- Search Widget -->
    <div class="card my-4">
        <h5 class="card-header">Search Experiments</h5>
        <div class="card-body">
            <div class="input-group">
                <input type="text" class="form-control" placeholder="Search experiments...">
                <span class="input-group-append">
                    <button class="btn btn-secondary" type="button">Search</button>
                </span>
            </div>
        </div>
    </div>

    <!-- Quick Links Widget -->
    <div class="card my-4">
        <h5 class="card-header">Quick Links</h5>
        <div class="card-body">
            <ul class="list-unstyled mb-0">
                <li><a href="/api/experiments/create">Create Experiment</a></li>
                <li><a href="/api-docs.php">API Documentation</a></li>
                <li><a href="/models.php">Model Registry</a></li>
            </ul>
        </div>
    </div>

    <!-- System Status Widget -->
    <div class="card my-4">
        <h5 class="card-header">System Status</h5>
        <div class="card-body">
            <p><span class="badge bg-success">Healthy</span> All systems operational</p>
            <small class="text-muted">
                <strong>Storage:</strong> file:///data/artifacts<br>
                <strong>Version:</strong> 2.11.2<br>
                <strong>Uptime:</strong> <span id="uptime">--</span>
            </small>
        </div>
    </div>
</div>

<script type="text/javascript">
    document.addEventListener('DOMContentLoaded', function() {
        let hours = Math.floor(Math.random() * 720) + 24;
        function updateUptime() {
            hours++;
            const days = Math.floor(hours / 24);
            const h = hours % 24;
            document.getElementById('uptime').innerText = days + 'd ' + h + 'h';
        }
        updateUptime();
        setInterval(updateUptime, 3600000);
    });
</script>
