<?php
$widget_title = "System Health Monitor";
$widget_brief = "Server performance metrics dashboard";

$widget_content = <<<HTML
<div class="container mt-4">
    <div class="card">
        <div class="card-header bg-success text-white">
            <h5>Health Monitor Widget</h5>
        </div>
        <div class="card-body">
            <div class="row">
                <div class="col-md-4">
                    <div class="card text-center mb-3">
                        <div class="card-body">
                            <h6>CPU Usage</h6>
                            <h2 class="text-primary">23%</h2>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card text-center mb-3">
                        <div class="card-body">
                            <h6>Memory</h6>
                            <h2 class="text-warning">67%</h2>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card text-center mb-3">
                        <div class="card-body">
                            <h6>Disk I/O</h6>
                            <h2 class="text-success">12%</h2>
                        </div>
                    </div>
                </div>
            </div>
            <p>Monitor your infrastructure health with real-time metrics and alerts.</p>
        </div>
    </div>
</div>
HTML;
?>
