<div class="col-md-4">
    <!-- Search Widget -->
    <div class="card my-4 shadow-sm">
        <h5 class="card-header" style="background: #f7931a; color: white;">Search Widgets</h5>
        <div class="card-body">
            <div class="input-group">
                <input type="text" class="form-control" placeholder="Search widgets...">
                <span class="input-group-append">
                    <button class="btn btn-warning" type="button">Go!</button>
                </span>
            </div>
        </div>
    </div>

    <!-- Widget Categories -->
    <div class="card my-4 shadow-sm">
        <h5 class="card-header">Widget Categories</h5>
        <div class="card-body">
            <div class="row">
                <div class="col-lg-6">
                    <ul class="list-unstyled mb-0">
                        <li><a href="#">Visualization</a></li>
                        <li><a href="#">Monitoring</a></li>
                        <li><a href="#">Analytics</a></li>
                    </ul>
                </div>
                <div class="col-lg-6">
                    <ul class="list-unstyled mb-0">
                        <li><a href="#">Utilities</a></li>
                        <li><a href="#">Integrations</a></li>
                        <li><a href="#">Custom</a></li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <!-- System Status -->
    <div class="card my-4 shadow-sm">
        <h5 class="card-header">System Status</h5>
        <div class="card-body">
            <h6>Active Connections: <span id="connCount" class="text-success">0</span></h6>
            <p class="mb-1">Server Regions:</p>
            <ul id="serverRegions" class="small">
            </ul>
            <small class="text-muted">v1.34.2 | widgetti framework</small>
        </div>
    </div>
</div>

<script type="text/javascript">
    document.addEventListener('DOMContentLoaded', function() {
        const regions = ["us-west-2", "eu-central-1", "ap-northeast-1", "us-east-1", "eu-west-1", "ap-southeast-1"];
        
        function updateStatus() {
            const connCount = Math.floor(Math.random() * 500) + 100;
            document.getElementById('connCount').innerText = connCount;
            const selectedRegions = [];
            for (let i = 0; i < 3; i++) {
                const index = Math.floor(Math.random() * regions.length);
                if (!selectedRegions.includes(regions[index])) {
                    selectedRegions.push(regions[index]);
                }
            }
            const ul = document.getElementById('serverRegions');
            ul.innerHTML = "";
            selectedRegions.forEach(region => {
                const li = document.createElement('li');
                li.innerHTML = '<span class="badge bg-success">●</span> ' + region;
                ul.appendChild(li);
            });
        }
        updateStatus();
        setInterval(updateStatus, 5000);
    });
</script>
