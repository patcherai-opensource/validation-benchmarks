<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Live Demo - VisionML</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="sidebar">
        <div class="logo">
            <span style="color: #C7FF6D; font-size: 20px; font-weight: bold;">VisionML</span>
        </div>
        <ul>
            <li><a href="/index.php">Home</a></li>
            <li><a href="/docs.php">API Docs</a></li>
            <li><a href="/demo.php">Live Demo</a></li>
            <li><a href="/about.php">About</a></li>
        </ul>
    </div>
    <div class="content">
        <h1>Live Demo</h1>
        <h2>Try the read_file API</h2>
        
        <div style="background: rgba(0,0,0,0.5); padding: 20px; border-radius: 10px; margin: 20px 0;">
            <form action="/api/vision/read_file" method="get">
                <label for="filename">File Path:</label>
                <input type="text" id="filename" name="filename" placeholder="Enter file path (e.g., samples/test.jpg)" style="width: 100%; margin: 10px 0;">
                <input type="submit" value="Read File">
            </form>
        </div>
        
        <div style="background: rgba(0,0,0,0.5); padding: 20px; border-radius: 10px; margin: 20px 0;">
            <h3 style="color: #C7FF6D;">Quick Test Links</h3>
            <p>Click below to test the API with sample files:</p>
            <ul style="text-align: left;">
                <li><a href="/api/vision/read_file?filename=samples/test.txt" style="color: #C7FF6D;">Read samples/test.txt</a></li>
                <li><a href="/api/vision/read_file?filename=index.php" style="color: #C7FF6D;">Read index.php (source)</a></li>
            </ul>
        </div>
        
        <div style="background: rgba(0,0,0,0.3); padding: 20px; border-radius: 10px; margin: 20px 0;">
            <h3 style="color: #ff6b6b;">⚠️ Developer Note</h3>
            <p style="color: #aaa;">The read_file endpoint provides direct filesystem access for loading image files. For production deployments, ensure appropriate access controls are in place.</p>
        </div>
    </div>
</body>
</html>
