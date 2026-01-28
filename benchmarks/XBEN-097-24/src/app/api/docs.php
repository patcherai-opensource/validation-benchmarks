<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Documentation - DataLabel Studio</title>
    <link rel="stylesheet" href="/style.css">
    <link rel="stylesheet" href="/static/css/main.css">
</head>
<body>
    <div class="sidebar">
        <div class="logo">
            <img src="/images/logo.png" width="120" height="100">
        </div>
        <ul>
            <li><a href="/">Dashboard</a></li>
            <li><a href="/projects.php">Projects</a></li>
            <li><a href="/tasks.php">Tasks</a></li>
            <li><a href="/export.php">Export</a></li>
            <li><a href="/about.php">About</a></li>
            <li><a href="/login.php">Login</a></li>
        </ul>
    </div>
    <div class="content">
        <h1>API Documentation</h1>
        <h2>DataLabel Studio REST API v2.4.1</h2>
        
        <h3>Authentication</h3>
        <p>All API requests require authentication using an API token:</p>
        <pre>
Authorization: Token your-api-token-here
        </pre>

        <h3>Base URL</h3>
        <pre>https://your-instance.datalabel.io/api/v1/</pre>

        <h3>Endpoints</h3>
        
        <h4>Projects</h4>
        <table>
            <tr><th>Method</th><th>Endpoint</th><th>Description</th></tr>
            <tr><td>GET</td><td>/api/v1/projects</td><td>List all projects</td></tr>
            <tr><td>POST</td><td>/api/v1/projects</td><td>Create a new project</td></tr>
            <tr><td>GET</td><td>/api/v1/projects/{id}</td><td>Get project details</td></tr>
            <tr><td>PUT</td><td>/api/v1/projects/{id}</td><td>Update project</td></tr>
            <tr><td>DELETE</td><td>/api/v1/projects/{id}</td><td>Delete project</td></tr>
        </table>

        <h4>Tasks</h4>
        <table>
            <tr><th>Method</th><th>Endpoint</th><th>Description</th></tr>
            <tr><td>GET</td><td>/api/v1/projects/{id}/tasks</td><td>List tasks</td></tr>
            <tr><td>POST</td><td>/api/v1/projects/{id}/tasks</td><td>Create task</td></tr>
            <tr><td>GET</td><td>/api/v1/tasks/{id}</td><td>Get task details</td></tr>
            <tr><td>POST</td><td>/api/v1/tasks/{id}/annotations</td><td>Submit annotation</td></tr>
        </table>

        <h4>Export</h4>
        <table>
            <tr><th>Method</th><th>Endpoint</th><th>Description</th></tr>
            <tr><td>GET</td><td>/api/v1/projects/{id}/export</td><td>Export annotations</td></tr>
        </table>

        <h4>Query Parameters for Export</h4>
        <ul>
            <li><code>format</code> - Export format (json, csv, coco, yolo)</li>
            <li><code>completed_only</code> - Only export completed tasks</li>
            <li><code>include_predictions</code> - Include ML predictions</li>
        </ul>

        <h3>Error Codes</h3>
        <table>
            <tr><th>Code</th><th>Description</th></tr>
            <tr><td>400</td><td>Bad Request</td></tr>
            <tr><td>401</td><td>Unauthorized</td></tr>
            <tr><td>403</td><td>Forbidden</td></tr>
            <tr><td>404</td><td>Not Found</td></tr>
            <tr><td>429</td><td>Rate Limited</td></tr>
            <tr><td>500</td><td>Internal Server Error</td></tr>
        </table>
    </div>
</body>
</html>
