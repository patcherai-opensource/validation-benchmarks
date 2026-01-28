<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Projects - DataLabel Studio</title>
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
        <h1>Projects</h1>
        <p>Please <a href="/login.php">sign in</a> to view your projects.</p>
        
        <h3>What are Projects?</h3>
        <p>
        Projects in DataLabel Studio organize your labeling tasks and data. Each project contains:
        </p>
        <ul>
            <li>Data sources (images, text, audio, video)</li>
            <li>Labeling configurations and templates</li>
            <li>Team member assignments</li>
            <li>Quality control settings</li>
            <li>Export configurations</li>
        </ul>

        <h3>Project Types</h3>
        <ul>
            <li><strong>Image Classification:</strong> Assign labels to entire images</li>
            <li><strong>Object Detection:</strong> Draw bounding boxes around objects</li>
            <li><strong>Image Segmentation:</strong> Pixel-level annotation for semantic segmentation</li>
            <li><strong>Text Classification:</strong> Categorize text documents</li>
            <li><strong>Named Entity Recognition:</strong> Tag entities in text</li>
            <li><strong>Audio Transcription:</strong> Transcribe and label audio files</li>
            <li><strong>Video Annotation:</strong> Frame-by-frame video labeling</li>
        </ul>
    </div>
</body>
</html>
