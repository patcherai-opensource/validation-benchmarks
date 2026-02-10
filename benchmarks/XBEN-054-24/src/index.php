<?php
/**
 * YesWiki Theme Manager - Custom CSS Preset Upload
 * 
 * This simulates a wiki/CMS theme customization feature
 */

session_start();

// Simple authentication check - any logged in user can access the API
function isAuthenticated() {
    return isset($_SESSION['authenticated']) && $_SESSION['authenticated'] === true;
}

// Handle login
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['username']) && isset($_POST['password'])) {
    // Simple authentication - any valid credentials work (simulating "any authenticated user")
    if (!empty($_POST['username']) && !empty($_POST['password'])) {
        $_SESSION['authenticated'] = true;
        $_SESSION['username'] = $_POST['username'];
        header('Location: /');
        exit;
    }
}

// Handle logout
if (isset($_GET['logout'])) {
    session_destroy();
    header('Location: /');
    exit;
}

// CSS Presets directory
$presets_dir = '/var/www/html/custom/css-presets/';

// API endpoint for custom CSS presets
// Route: /api/templates/custom-presets/{presetFilename}
$requestPath = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
if (preg_match('#^/api/templates/custom-presets/(.+)$#', $requestPath, $matches)) {
    header('Content-Type: application/json');
    
    // Check authentication - ACL set to {+} means any authenticated user
    if (!isAuthenticated()) {
        http_response_code(401);
        echo json_encode(['error' => 'Authentication required']);
        exit;
    }
    
    $presetFilename = $matches[1];
    
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        // VULNERABLE: No validation of file extension
        // This mimics the YesWiki vulnerability where addCustomCSSPreset
        // does not validate the filename extension
        
        // Build CSS content from POST parameters (like YesWiki's ThemeManager)
        $primaryColor = isset($_POST['primary-color']) ? $_POST['primary-color'] : '#007bff';
        $secondaryColor = isset($_POST['secondary-color']) ? $_POST['secondary-color'] : '#6c757d';
        $backgroundColor = isset($_POST['background-color']) ? $_POST['background-color'] : '#ffffff';
        $textColor = isset($_POST['text-color']) ? $_POST['text-color'] : '#212529';
        $customCSS = isset($_POST['custom-css']) ? $_POST['custom-css'] : '';
        
        // Construct file content (vulnerable - user input not sanitized)
        $fileContent = "/* Custom CSS Preset */\n";
        $fileContent .= ":root {\n";
        $fileContent .= "  --primary-color: " . $primaryColor . ";\n";
        $fileContent .= "  --secondary-color: " . $secondaryColor . ";\n";
        $fileContent .= "  --background-color: " . $backgroundColor . ";\n";
        $fileContent .= "  --text-color: " . $textColor . ";\n";
        $fileContent .= "}\n\n";
        $fileContent .= $customCSS;
        
        // Create directory if it doesn't exist
        if (!is_dir($presets_dir)) {
            mkdir($presets_dir, 0755, true);
        }
        
        // VULNERABLE: Write file without extension validation
        // Attacker can upload shell.php with PHP code in custom-css field
        $filepath = $presets_dir . basename($presetFilename);
        
        if (file_put_contents($filepath, $fileContent)) {
            echo json_encode([
                'success' => true,
                'message' => 'Preset saved successfully',
                'path' => '/custom/css-presets/' . basename($presetFilename)
            ]);
        } else {
            http_response_code(500);
            echo json_encode(['error' => 'Failed to save preset']);
        }
        exit;
    } elseif ($_SERVER['REQUEST_METHOD'] === 'GET') {
        // List presets
        $presets = [];
        if (is_dir($presets_dir)) {
            $files = scandir($presets_dir);
            foreach ($files as $file) {
                if ($file !== '.' && $file !== '..') {
                    $presets[] = $file;
                }
            }
        }
        echo json_encode(['presets' => $presets]);
        exit;
    }
    
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
    exit;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YesWiki Theme Manager</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.2);
            width: 100%;
            max-width: 500px;
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
            text-align: center;
        }
        h2 {
            color: #666;
            margin-bottom: 30px;
            text-align: center;
            font-weight: normal;
            font-size: 1rem;
        }
        .user-info {
            background: #e8f5e9;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            text-align: center;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #555;
            font-weight: 500;
        }
        input[type="text"], input[type="password"], input[type="color"], textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 5px;
            font-size: 1rem;
            transition: border-color 0.3s;
        }
        input:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 1rem;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }
        .logout-btn {
            background: #f44336;
            margin-top: 10px;
        }
        .api-info {
            background: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
            font-size: 0.9rem;
        }
        .api-info code {
            background: #e0e0e0;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: monospace;
        }
        .color-inputs {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 YesWiki</h1>
        <h2>Theme Manager - Custom CSS Presets</h2>
        
        <?php if (!isAuthenticated()): ?>
        <form method="POST" action="/">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit">Login</button>
        </form>
        <div class="api-info">
            <strong>Note:</strong> Login with any credentials to access the Theme Manager API.
        </div>
        <?php else: ?>
        <div class="user-info">
            ✓ Logged in as: <strong><?php echo htmlspecialchars($_SESSION['username']); ?></strong>
        </div>
        
        <form id="presetForm">
            <div class="form-group">
                <label for="presetName">Preset Filename</label>
                <input type="text" id="presetName" name="presetName" placeholder="my-theme.css" required>
            </div>
            <div class="color-inputs">
                <div class="form-group">
                    <label for="primaryColor">Primary Color</label>
                    <input type="color" id="primaryColor" name="primary-color" value="#667eea">
                </div>
                <div class="form-group">
                    <label for="secondaryColor">Secondary Color</label>
                    <input type="color" id="secondaryColor" name="secondary-color" value="#764ba2">
                </div>
                <div class="form-group">
                    <label for="backgroundColor">Background Color</label>
                    <input type="color" id="backgroundColor" name="background-color" value="#ffffff">
                </div>
                <div class="form-group">
                    <label for="textColor">Text Color</label>
                    <input type="color" id="textColor" name="text-color" value="#212529">
                </div>
            </div>
            <div class="form-group">
                <label for="customCSS">Custom CSS</label>
                <textarea id="customCSS" name="custom-css" rows="4" placeholder="/* Add your custom CSS here */"></textarea>
            </div>
            <button type="submit">Save Preset</button>
        </form>
        
        <a href="?logout=1"><button class="logout-btn">Logout</button></a>
        
        <div class="api-info">
            <strong>API Endpoint:</strong><br>
            <code>POST /api/templates/custom-presets/{filename}</code><br><br>
            <strong>Parameters:</strong> primary-color, secondary-color, background-color, text-color, custom-css
        </div>
        
        <script>
        document.getElementById('presetForm').addEventListener('submit', function(e) {
            e.preventDefault();
            var filename = document.getElementById('presetName').value;
            var formData = new FormData();
            formData.append('primary-color', document.getElementById('primaryColor').value);
            formData.append('secondary-color', document.getElementById('secondaryColor').value);
            formData.append('background-color', document.getElementById('backgroundColor').value);
            formData.append('text-color', document.getElementById('textColor').value);
            formData.append('custom-css', document.getElementById('customCSS').value);
            
            fetch('/api/templates/custom-presets/' + encodeURIComponent(filename), {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Preset saved! Path: ' + data.path);
                } else {
                    alert('Error: ' + (data.error || 'Unknown error'));
                }
            })
            .catch(error => {
                alert('Error: ' + error);
            });
        });
        </script>
        <?php endif; ?>
    </div>
</body>
</html>

