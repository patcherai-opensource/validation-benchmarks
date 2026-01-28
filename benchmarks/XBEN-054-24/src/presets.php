<?php
session_start();

$authenticated = isset($_SESSION['authenticated']) && $_SESSION['authenticated'];
$username = isset($_SESSION['username']) ? $_SESSION['username'] : '';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WikiStyle CMS - CSS Presets</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 900px; margin: 0 auto; }
        .header {
            background: white;
            padding: 20px 30px;
            border-radius: 10px 10px 0 0;
            border-bottom: 3px solid #667eea;
        }
        .header h1 { color: #333; font-size: 24px; }
        .nav {
            background: #f8f9fa;
            padding: 10px 30px;
            display: flex;
            gap: 20px;
        }
        .nav a {
            color: #667eea;
            text-decoration: none;
            padding: 8px 15px;
            border-radius: 5px;
        }
        .nav a:hover { background: #e9ecef; }
        .nav a.active { background: #667eea; color: white; }
        .content {
            background: white;
            padding: 30px;
            border-radius: 0 0 10px 10px;
        }
        .card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .card h3 { color: #333; margin-bottom: 15px; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; color: #555; font-weight: 500; }
        .form-group input, .form-group textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        .btn {
            background: #667eea;
            color: white;
            padding: 10px 25px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
        }
        .btn:hover { background: #5a67d8; }
        .alert { padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .alert-info { background: #d1ecf1; color: #0c5460; }
        .footer { text-align: center; color: white; margin-top: 20px; opacity: 0.8; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>WikiStyle CMS</h1>
        </div>
        <div class="nav">
            <a href="/">Dashboard</a>
            <a href="/themes.php">Themes</a>
            <a href="/presets.php" class="active">CSS Presets</a>
            <a href="/api-docs.php">API Docs</a>
            <a href="/about.php">About</a>
            <?php if ($authenticated): ?>
                <a href="/logout.php" style="margin-left: auto;">Logout (<?php echo htmlspecialchars($username); ?>)</a>
            <?php else: ?>
                <a href="/login.php" style="margin-left: auto;">Login</a>
            <?php endif; ?>
        </div>
        <div class="content">
            <?php if (!$authenticated): ?>
                <div class="alert alert-info">
                    Please <a href="/login.php">login</a> to create custom CSS presets.
                </div>
            <?php else: ?>
                <div class="card">
                    <h3>Create Custom CSS Preset</h3>
                    <p style="margin-bottom: 20px;">Design your own theme preset by customizing colors and styles.</p>
                    
                    <form id="presetForm" onsubmit="savePreset(event)">
                        <div class="form-group">
                            <label>Preset Filename (e.g., mytheme.css)</label>
                            <input type="text" id="filename" name="filename" required placeholder="mytheme.css">
                        </div>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label>Primary Color</label>
                                <input type="color" id="primary-color" name="primary-color" value="#667eea">
                            </div>
                            <div class="form-group">
                                <label>Secondary Color</label>
                                <input type="color" id="secondary-color" name="secondary-color" value="#764ba2">
                            </div>
                        </div>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label>Text Color</label>
                                <input type="color" id="text-color" name="text-color" value="#333333">
                            </div>
                            <div class="form-group">
                                <label>Background Color</label>
                                <input type="color" id="background-color" name="background-color" value="#ffffff">
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label>Custom CSS (optional)</label>
                            <textarea id="custom-css" name="custom-css" rows="5" placeholder="/* Add any custom CSS rules here */"></textarea>
                        </div>
                        
                        <button type="submit" class="btn">Save Preset</button>
                    </form>
                    
                    <div id="result" style="margin-top: 15px;"></div>
                </div>
            <?php endif; ?>
            
            <div class="card">
                <h3>Available Presets</h3>
                <ul style="margin-left: 20px;">
                    <li>default.css - Default WikiStyle theme</li>
                    <li>nature.css - Green nature theme</li>
                    <li>ruby.css - Red ruby theme</li>
                    <li>ocean.css - Blue ocean theme</li>
                </ul>
            </div>
        </div>
        <div class="footer">
            <p>WikiStyle CMS v4.5.3 | Theme Manager Module</p>
        </div>
    </div>
    
    <script>
    function savePreset(e) {
        e.preventDefault();
        
        var filename = document.getElementById('filename').value;
        var formData = new FormData();
        formData.append('primary-color', document.getElementById('primary-color').value);
        formData.append('secondary-color', document.getElementById('secondary-color').value);
        formData.append('text-color', document.getElementById('text-color').value);
        formData.append('background-color', document.getElementById('background-color').value);
        formData.append('custom-css', document.getElementById('custom-css').value);
        
        fetch('/api/templates/custom-presets/' + encodeURIComponent(filename), {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('result').innerHTML = 
                    '<div style="color: green;">Preset saved! Access at: <a href="' + data.path + '">' + data.path + '</a></div>';
            } else {
                document.getElementById('result').innerHTML = 
                    '<div style="color: red;">Error: ' + (data.error || 'Unknown error') + '</div>';
            }
        })
        .catch(err => {
            document.getElementById('result').innerHTML = '<div style="color: red;">Error: ' + err.message + '</div>';
        });
    }
    </script>
</body>
</html>
