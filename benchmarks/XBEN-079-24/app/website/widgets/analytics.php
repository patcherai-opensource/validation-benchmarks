<?php
$widget_title = "Analytics Dashboard";
$widget_brief = "Comprehensive analytics with drill-down capabilities";

$widget_content = <<<HTML
<div class="container mt-4">
    <div class="card">
        <div class="card-header bg-primary text-white">
            <h5>Analytics Dashboard Widget</h5>
        </div>
        <div class="card-body">
            <p>Full-featured analytics suite for your data needs:</p>
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Metric</th>
                        <th>Today</th>
                        <th>This Week</th>
                        <th>Trend</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Page Views</td>
                        <td>1,234</td>
                        <td>8,901</td>
                        <td><span class="text-success">↑ 12%</span></td>
                    </tr>
                    <tr>
                        <td>Unique Users</td>
                        <td>456</td>
                        <td>3,210</td>
                        <td><span class="text-success">↑ 8%</span></td>
                    </tr>
                    <tr>
                        <td>API Calls</td>
                        <td>12,345</td>
                        <td>89,012</td>
                        <td><span class="text-danger">↓ 3%</span></td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</div>
HTML;
?>
