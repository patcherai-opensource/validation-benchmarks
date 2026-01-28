<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tasks - DataLabel Studio</title>
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
        <h1>My Tasks</h1>
        <p>Please <a href="/login.php">sign in</a> to view your assigned tasks.</p>
        
        <h3>Task Queue</h3>
        <p>
        Tasks are individual labeling assignments within a project. When you're assigned to a project, 
        tasks will appear in your queue for completion.
        </p>

        <h3>Task Status Types</h3>
        <ul>
            <li><strong>Pending:</strong> Not yet started</li>
            <li><strong>In Progress:</strong> Currently being labeled</li>
            <li><strong>Completed:</strong> Annotation finished, pending review</li>
            <li><strong>Reviewed:</strong> Quality checked and approved</li>
            <li><strong>Rejected:</strong> Needs re-labeling</li>
        </ul>

        <h3>Keyboard Shortcuts</h3>
        <p>Speed up your labeling with these shortcuts:</p>
        <ul>
            <li><code>Ctrl+S</code> - Save current annotation</li>
            <li><code>Arrow Left/Right</code> - Navigate between tasks</li>
            <li><code>1-9</code> - Quick label selection</li>
            <li><code>Ctrl+Z</code> - Undo last action</li>
            <li><code>Space</code> - Toggle playback (audio/video)</li>
        </ul>
    </div>
</body>
</html>
