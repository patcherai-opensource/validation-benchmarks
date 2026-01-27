<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DataAnnotate - Data Labeling Platform</title>
    <link rel="stylesheet" href="/static/css/main.css">
    <script src="/static/js/app.js"></script>
</head>
<body>
    <header class="header">
        <h1>DataAnnotate</h1>
        <nav class="nav-links">
            <a href="/">Dashboard</a>
            <a href="/projects.php">Projects</a>
            <a href="/docs.php">Documentation</a>
            <a href="/login.php">Sign In</a>
        </nav>
    </header>
    
    <div class="container">
        <div class="card">
            <h2>Welcome to DataAnnotate</h2>
            <p>The open-source data labeling platform for machine learning teams. Label images, text, audio and video with intelligent assistance.</p>
        </div>
        
        <div class="card">
            <h3>Quick Start</h3>
            <p>Get started with your data labeling projects in minutes:</p>
            <ol>
                <li>Create a new project and configure your labeling interface</li>
                <li>Import your data from local storage or cloud providers</li>
                <li>Invite team members or use our ML-assisted labeling</li>
                <li>Export annotations in popular formats (COCO, YOLO, Pascal VOC)</li>
            </ol>
            <a href="/login.php" class="btn">Get Started</a>
        </div>
        
        <h3>Featured Capabilities</h3>
        <div class="project-grid">
            <div class="project-card">
                <h4>Image Annotation</h4>
                <p>Bounding boxes, polygons, semantic segmentation, and keypoint detection for computer vision projects.</p>
            </div>
            <div class="project-card">
                <h4>Text Labeling</h4>
                <p>Named entity recognition, text classification, sentiment analysis, and relation extraction.</p>
            </div>
            <div class="project-card">
                <h4>Audio Transcription</h4>
                <p>Speech-to-text, speaker diarization, and audio classification with waveform visualization.</p>
            </div>
            <div class="project-card">
                <h4>ML-Assisted Labeling</h4>
                <p>Connect your ML backend to auto-label data and accelerate your annotation workflow.</p>
            </div>
        </div>
        
        <div class="card">
            <h3>API Integration</h3>
            <p>DataAnnotate provides a comprehensive REST API for automation and integration with your ML pipelines.</p>
            <pre style="background: #f1f5f9; padding: 15px; border-radius: 5px; overflow-x: auto;">
# Example: List all projects
curl -X GET "http://localhost:8080/api/projects" \
     -H "Authorization: Token YOUR_API_KEY"

# Example: Export annotations
curl -X GET "http://localhost:8080/api/projects/1/export?format=COCO" \
     -H "Authorization: Token YOUR_API_KEY"
            </pre>
        </div>
    </div>
    
    <footer>
        <p>&copy; 2024 DataAnnotate Platform v2.1.0 | <a href="/docs.php">API Docs</a> | <a href="https://github.com/dataannotate/dataannotate">GitHub</a></p>
    </footer>
</body>
</html>

