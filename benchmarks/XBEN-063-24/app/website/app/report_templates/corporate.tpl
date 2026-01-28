<!DOCTYPE html>
<html>
<head>
    <title>{{title}} - Corporate Report</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, sans-serif; margin: 0; padding: 0; }
        .banner { background: #003366; color: white; padding: 20px; }
        .main { padding: 30px; }
        .meta { background: #f0f0f0; padding: 15px; margin: 20px 0; }
        .content { line-height: 1.6; }
    </style>
</head>
<body>
    <div class="banner">
        <h1>{{title}}</h1>
    </div>
    <div class="main">
        <div class="meta">
            <strong>Prepared by:</strong> {{author}}<br>
            <strong>Date:</strong> {{date}}
        </div>
        <div class="content">
            {{content}}
        </div>
    </div>
</body>
</html>
