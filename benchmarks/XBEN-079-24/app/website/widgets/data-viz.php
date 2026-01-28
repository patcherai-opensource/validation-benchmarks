<?php
$widget_title = "Real-Time Data Visualization";
$widget_brief = "Interactive charts and graphs for live data monitoring";

$widget_content = <<<HTML
<div class="container mt-4">
    <div class="card">
        <div class="card-header bg-warning text-dark">
            <h5>Data Visualization Widget</h5>
        </div>
        <div class="card-body">
            <p>This widget provides real-time data visualization capabilities with the following features:</p>
            <ul>
                <li>Live streaming data charts</li>
                <li>Customizable refresh intervals</li>
                <li>Multiple chart types (line, bar, pie, scatter)</li>
                <li>Data export to CSV/JSON formats</li>
            </ul>
            <div class="alert alert-info">
                <strong>Note:</strong> Connect your data source via the API endpoint to enable real-time updates.
            </div>
        </div>
    </div>
</div>
HTML;
?>
