<div class="col-md-4">
    <div class="card my-4">
        <h5 class="card-header"><i class="bi bi-speedometer2"></i> Quick Stats</h5>
        <div class="card-body">
            <?php
            $stats_file = '/var/lib/mltrack/experiments.json';
            $exp_count = 0;
            if (file_exists($stats_file)) {
                $data = json_decode(file_get_contents($stats_file), true);
                $exp_count = is_array($data) ? count($data) : 0;
            }
            ?>
            <div class="d-flex justify-content-between mb-2">
                <span>Total Experiments</span>
                <span class="badge bg-primary"><?= $exp_count; ?></span>
            </div>
            <div class="d-flex justify-content-between mb-2">
                <span>Active Runs</span>
                <span class="badge bg-success">0</span>
            </div>
            <div class="d-flex justify-content-between">
                <span>Models Registered</span>
                <span class="badge bg-info">0</span>
            </div>
        </div>
    </div>

    <div class="card my-4">
        <h5 class="card-header"><i class="bi bi-lightning"></i> Quick Actions</h5>
        <div class="card-body">
            <div class="d-grid gap-2">
                <a href="/experiments.php?action=create" class="btn btn-outline-success btn-sm">
                    <i class="bi bi-plus-circle"></i> New Experiment
                </a>
                <a href="/docs.php" class="btn btn-outline-primary btn-sm">
                    <i class="bi bi-book"></i> API Documentation
                </a>
            </div>
        </div>
    </div>

    <div class="card my-4">
        <h5 class="card-header"><i class="bi bi-info-circle"></i> About MLTrack</h5>
        <div class="card-body">
            <p class="small text-muted mb-2">
                MLTrack is an open-source platform for ML experiment tracking, model versioning, and deployment.
            </p>
            <p class="small text-muted mb-0">
                Version: 2.11.2
            </p>
        </div>
    </div>
</div>
