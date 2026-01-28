<?php
$widget_title = "Resource Allocator";
$widget_brief = "Cloud infrastructure management";

$widget_content = <<<HTML
<div class="container mt-4">
    <div class="card">
        <div class="card-header bg-info text-white">
            <h5>Resource Allocator Widget</h5>
        </div>
        <div class="card-body">
            <h6>Current Resource Allocation</h6>
            <div class="progress mb-3" style="height: 25px;">
                <div class="progress-bar bg-primary" role="progressbar" style="width: 45%">CPU: 45%</div>
            </div>
            <div class="progress mb-3" style="height: 25px;">
                <div class="progress-bar bg-warning" role="progressbar" style="width: 72%">Memory: 72%</div>
            </div>
            <div class="progress mb-3" style="height: 25px;">
                <div class="progress-bar bg-success" role="progressbar" style="width: 28%">Storage: 28%</div>
            </div>
            <hr>
            <h6>Auto-Scaling Status</h6>
            <p><span class="badge bg-success">ENABLED</span> Minimum: 2 | Maximum: 10 | Current: 4</p>
        </div>
    </div>
</div>
HTML;
?>
