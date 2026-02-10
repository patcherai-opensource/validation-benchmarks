INDEX_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Label Studio</title>
    <link rel="stylesheet" href="/static/css/label-studio.css">
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand">
            <a href="/">Label Studio</a>
        </div>
        <ul class="nav-links">
            <li><a href="/projects/">Projects</a></li>
            <li><a href="/user/account/">Account</a></li>
        </ul>
    </nav>
    <div class="container">
        <div class="hero">
            <h1>Welcome to Label Studio</h1>
            <p>The most flexible data labeling tool for machine learning projects.</p>
            <div class="cta-buttons">
                <a href="/projects/create/" class="btn btn-primary">Create New Project</a>
                <a href="/projects/" class="btn btn-secondary">View Projects</a>
            </div>
        </div>
        <div class="features">
            <div class="feature-card">
                <h3>Multi-type Data</h3>
                <p>Label images, audio, text, and more with a single tool.</p>
            </div>
            <div class="feature-card">
                <h3>Custom Templates</h3>
                <p>Create custom labeling interfaces with our XML-based configuration.</p>
            </div>
            <div class="feature-card">
                <h3>Team Collaboration</h3>
                <p>Work together with your team on labeling projects.</p>
            </div>
        </div>
    </div>
    <footer>
        <p>&copy; 2024 Label Studio. Open Source Data Labeling.</p>
    </footer>
</body>
</html>
"""

PROJECTS_LIST_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Projects - Label Studio</title>
    <link rel="stylesheet" href="/static/css/label-studio.css">
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand">
            <a href="/">Label Studio</a>
        </div>
        <ul class="nav-links">
            <li><a href="/projects/" class="active">Projects</a></li>
            <li><a href="/user/account/">Account</a></li>
        </ul>
    </nav>
    <div class="container">
        <div class="page-header">
            <h1>Your Projects</h1>
            <a href="/projects/create/" class="btn btn-primary">New Project</a>
        </div>
        <div class="projects-grid">
            <div class="project-card">
                <h3>Text Classification</h3>
                <p>Sentiment analysis dataset</p>
                <span class="badge">1,250 tasks</span>
            </div>
            <div class="project-card">
                <h3>Image Annotation</h3>
                <p>Object detection training data</p>
                <span class="badge">843 tasks</span>
            </div>
            <div class="project-card">
                <h3>NER Task</h3>
                <p>Named entity recognition</p>
                <span class="badge">2,100 tasks</span>
            </div>
        </div>
    </div>
</body>
</html>
"""

CREATE_PROJECT_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Create Project - Label Studio</title>
    <link rel="stylesheet" href="/static/css/label-studio.css">
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand">
            <a href="/">Label Studio</a>
        </div>
        <ul class="nav-links">
            <li><a href="/projects/">Projects</a></li>
            <li><a href="/user/account/">Account</a></li>
        </ul>
    </nav>
    <div class="container">
        <div class="page-header">
            <h1>Create New Project</h1>
        </div>
        <form class="project-form" method="POST">
            <div class="form-group">
                <label for="project_name">Project Name</label>
                <input type="text" id="project_name" name="project_name" placeholder="Enter project name" required>
            </div>
            <div class="form-group">
                <label for="description">Description</label>
                <textarea id="description" name="description" placeholder="Describe your project"></textarea>
            </div>
            <button type="submit" class="btn btn-primary">Create Project</button>
        </form>
    </div>
</body>
</html>
"""

UPLOAD_EXAMPLE_FORM = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Upload Example - Label Studio</title>
    <link rel="stylesheet" href="/static/css/label-studio.css">
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand">
            <a href="/">Label Studio</a>
        </div>
        <ul class="nav-links">
            <li><a href="/projects/">Projects</a></li>
            <li><a href="/user/account/">Account</a></li>
        </ul>
    </nav>
    <div class="container">
        <div class="page-header">
            <h1>Upload Example Configuration</h1>
            <p>Test your labeling configuration with sample data.</p>
        </div>
        <form class="config-form" method="POST">
            <div class="form-group">
                <label for="label_config">Label Configuration (XML)</label>
                <textarea id="label_config" name="label_config" rows="10" placeholder="<View>
  <Text name=&quot;text&quot; value=&quot;$text&quot;/>
  <Choices name=&quot;sentiment&quot; toName=&quot;text&quot;>
    <Choice value=&quot;Positive&quot;/>
    <Choice value=&quot;Negative&quot;/>
  </Choices>
</View>"></textarea>
            </div>
            <button type="submit" class="btn btn-primary">Generate Example</button>
        </form>
        <div class="info-box">
            <h4>Configuration Format</h4>
            <p>Use XML to define your labeling interface. Variables like <code>$text</code> will be replaced with sample content.</p>
        </div>
    </div>
</body>
</html>
"""

TASK_PREVIEW_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Task Preview - Label Studio</title>
    <link rel="stylesheet" href="/static/css/label-studio.css">
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand">
            <a href="/">Label Studio</a>
        </div>
    </nav>
    <div class="container">
        <h1>Task Preview</h1>
        <div class="preview-section">
            <h3>Configuration</h3>
            <div class="config-display">{0}</div>
        </div>
        <div class="preview-section">
            <h3>Generated Task Data</h3>
            <div class="task-display">{1}</div>
        </div>
    </div>
</body>
</html>
"""

USER_ACCOUNT_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Account - Label Studio</title>
    <link rel="stylesheet" href="/static/css/label-studio.css">
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand">
            <a href="/">Label Studio</a>
        </div>
        <ul class="nav-links">
            <li><a href="/projects/">Projects</a></li>
            <li><a href="/user/account/" class="active">Account</a></li>
        </ul>
    </nav>
    <div class="container">
        <div class="page-header">
            <h1>Account Settings</h1>
        </div>
        <div class="account-info">
            <div class="info-row">
                <label>Username:</label>
                <span>admin</span>
            </div>
            <div class="info-row">
                <label>Email:</label>
                <span>admin@labelstudio.local</span>
            </div>
            <div class="info-row">
                <label>Role:</label>
                <span>Administrator</span>
            </div>
        </div>
    </div>
</body>
</html>
"""

