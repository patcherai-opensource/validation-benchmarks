<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Projects - DataAnnotate</title>
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
            <h2>Your Projects</h2>
            <p>Sign in to view and manage your labeling projects.</p>
            <a href="/login.php" class="btn">Sign In to Continue</a>
        </div>
        
        <div class="card">
            <h3>Demo Projects</h3>
            <p>Explore our demo projects to see DataAnnotate in action:</p>
        </div>
        
        <div class="project-grid">
            <div class="project-card">
                <h4>Image Classification Demo</h4>
                <p>1,000 images labeled for object detection</p>
                <small>Created: 2024-01-15 | 5 annotators</small>
            </div>
            <div class="project-card">
                <h4>NER Training Data</h4>
                <p>10,000 text samples with entity annotations</p>
                <small>Created: 2024-01-10 | 3 annotators</small>
            </div>
            <div class="project-card">
                <h4>Audio Transcription</h4>
                <p>500 audio clips with transcriptions</p>
                <small>Created: 2024-01-05 | 2 annotators</small>
            </div>
        </div>
    </div>
    
    <footer>
        <p>&copy; 2024 DataAnnotate Platform v2.1.0</p>
    </footer>
</body>
</html>
