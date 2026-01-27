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

    <!-- Server Status Widget -->
    <div class="card my-4">
        <h5 class="card-header">Server Status</h5>
        <div class="card-body">
            <ul class="list-unstyled mb-0">
                <li><span class="badge bg-success">●</span> API Server: Online</li>
                <li><span class="badge bg-success">●</span> Artifact Store: Connected</li>
                <li><span class="badge bg-success">●</span> Model Registry: Active</li>
            </ul>
            <hr>
            <small class="text-muted">Artifact Backend: Local Filesystem</small>
        </div>
    </div>

    <!-- Quick Links Widget -->
    <div class="card my-4">
        <h5 class="card-header">Quick Links</h5>
        <div class="card-body">
            <ul class="list-unstyled mb-0">
                <li><a href="/api-docs.php">API Documentation</a></li>
                <li><a href="/models.php">Model Registry</a></li>
                <li><a href="/index.php">Experiments</a></li>
            </ul>
        </div>
    </div>

    <!-- Active Runs Widget -->
    <div class="card my-4">
        <h5 class="card-header">Active Runs</h5>
        <div class="card-body">
            <h6>Running: <span id="runCount">0</span></h6>
            <p class="mb-0">Queued: <span id="queuedCount">0</span></p>
        </div>
    </div>
</div>

<script type="text/javascript">
    document.addEventListener('DOMContentLoaded', function() {
        function updateStats() {
            const runCount = Math.floor(Math.random() * 10) + 2;
            const queuedCount = Math.floor(Math.random() * 5);
            document.getElementById('runCount').innerText = runCount;
            document.getElementById('queuedCount').innerText = queuedCount;
        }
        updateStats();
        setInterval(updateStats, 5000);
    });
</script>
