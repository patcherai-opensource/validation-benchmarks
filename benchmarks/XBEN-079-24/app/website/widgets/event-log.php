<?php
$widget_title = "Event Log Viewer";
$widget_brief = "Real-time event log monitoring";

$widget_content = <<<HTML
<div class="container mt-4">
    <div class="card">
        <div class="card-header bg-dark text-white">
            <h5>Event Log Viewer Widget</h5>
        </div>
        <div class="card-body">
            <div class="table-responsive">
                <table class="table table-sm table-hover">
                    <thead>
                        <tr>
                            <th>Timestamp</th>
                            <th>Level</th>
                            <th>Source</th>
                            <th>Message</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td class="text-muted">2024-01-15 10:23:45</td>
                            <td><span class="badge bg-info">INFO</span></td>
                            <td>cdn.php</td>
                            <td>Asset served: widget-styles.css</td>
                        </tr>
                        <tr>
                            <td class="text-muted">2024-01-15 10:23:44</td>
                            <td><span class="badge bg-success">DEBUG</span></td>
                            <td>widget.php</td>
                            <td>Widget loaded: data-viz</td>
                        </tr>
                        <tr>
                            <td class="text-muted">2024-01-15 10:23:40</td>
                            <td><span class="badge bg-warning">WARN</span></td>
                            <td>cdn.php</td>
                            <td>Cache miss for asset</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>
HTML;
?>
