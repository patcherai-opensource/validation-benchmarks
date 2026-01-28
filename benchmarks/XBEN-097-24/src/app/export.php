<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Export - DataLabel Studio</title>
    <link rel="stylesheet" href="style.css">
    <link rel="stylesheet" href="/static/css/main.css">
</head>
<body>
    <div class="sidebar">
        <div class="logo">
            <img src="images/logo.png" width="120" height="100">
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
        <h1>Export Annotations</h1>
        <p>Please <a href="/login.php">sign in</a> to export your annotations.</p>
        
        <h3>Supported Export Formats</h3>
        <ul>
            <li><strong>JSON:</strong> Native DataLabel Studio format</li>
            <li><strong>CSV:</strong> Tabular data format</li>
            <li><strong>COCO:</strong> Microsoft COCO format for object detection</li>
            <li><strong>YOLO:</strong> YOLO darknet format</li>
            <li><strong>Pascal VOC:</strong> XML format for image classification</li>
            <li><strong>TSV:</strong> Tab-separated values</li>
            <li><strong>Custom:</strong> Define your own export template</li>
        </ul>

        <h3>Export API</h3>
        <p>
        Programmatically export annotations using our REST API:
        </p>
        <pre>
GET /api/v1/projects/{id}/export?format=json

Authorization: Token {your-api-token}
        </pre>

        <h3>Webhook Integration</h3>
        <p>
        Configure webhooks to automatically push annotations to your ML pipeline 
        when tasks are completed.
        </p>
    </div>
</body>
</html>
