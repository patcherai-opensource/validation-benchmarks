<div class="col-md-4">
    <!-- Search Widget -->
    <div class="card my-4">
        <h5 class="card-header">Search Experiments</h5>
        <div class="card-body">
            <div class="input-group">
                <input type="text" class="form-control" placeholder="Search experiments...">
                <span class="input-group-append">
                    <button class="btn btn-secondary" type="button">Go!</button>
                </span>
            </div>
        </div>
    </div>

    <!-- Frameworks Widget -->
    <div class="card my-4">
        <h5 class="card-header">Frameworks</h5>
        <div class="card-body">
            <div class="row">
                <div class="col-lg-6">
                    <ul class="list-unstyled mb-0">
                        <li><a href="#">PyTorch</a></li>
                        <li><a href="#">TensorFlow</a></li>
                        <li><a href="#">Keras</a></li>
                    </ul>
                </div>
                <div class="col-lg-6">
                    <ul class="list-unstyled mb-0">
                        <li><a href="#">Scikit-learn</a></li>
                        <li><a href="#">Hugging Face</a></li>
                        <li><a href="#">JAX</a></li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <!-- System Status Widget -->
    <div class="card my-4">
        <h5 class="card-header">System Status</h5>
        <div class="card-body">
            <h6>Active Runs: <span id="activeRuns">0</span></h6>
            <p>GPU Utilization:</p>
            <div class="progress mb-2">
                <div class="progress-bar bg-success" id="gpuBar" role="progressbar" style="width: 0%"></div>
            </div>
            <small class="text-muted">Artifact Storage: 847 GB / 2 TB</small>
        </div>
    </div>
</div>

<script type="text/javascript">
    document.addEventListener('DOMContentLoaded', function() {
        function updateStatus() {
            const activeRuns = Math.floor(Math.random() * 15) + 2;
            document.getElementById('activeRuns').innerText = activeRuns;
            
            const gpuUtil = Math.floor(Math.random() * 60) + 20;
            const gpuBar = document.getElementById('gpuBar');
            gpuBar.style.width = gpuUtil + '%';
            gpuBar.innerText = gpuUtil + '%';
        }
        updateStatus();
        setInterval(updateStatus, 5000);
    });
</script>
