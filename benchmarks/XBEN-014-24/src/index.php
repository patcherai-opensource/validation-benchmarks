<?php
// DBAdmin - Database Administration Tool
// Configuration loaded from environment

$flag = "@FLAG@";

// OAuth2 Configuration - used for SSO authentication
$oauth2_config = array(
    'OAUTH2_NAME' => 'corporate-sso',
    'OAUTH2_DISPLAY_NAME' => 'Corporate SSO',
    'OAUTH2_BUTTON_COLOR' => '#3366CC',
    'OAUTH2_ICON' => 'fa-key',
    'OAUTH2_CLIENT_ID' => 'dbadmin-prod-client',
    'OAUTH2_CLIENT_SECRET' => 'xK9#mP2$vL5nQ8@jR3wT6yU1',
    'OAUTH2_TOKEN_URL' => '/oauth/token',
    'OAUTH2_AUTHORIZATION_URL' => '/oauth/authorize',
    'OAUTH2_API_BASE_URL' => '/api/v1',
    'OAUTH2_USERINFO_ENDPOINT' => '/userinfo',
    'OAUTH2_SERVER_METADATA_URL' => null,
    'OAUTH2_SCOPE' => 'openid profile email',
    'OAUTH2_SSL_CERT_VERIFICATION' => true,
    'OAUTH2_LOGOUT_REDIRECT' => '/login'
);

// Handle API authentication endpoint
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_GET['action']) && $_GET['action'] === 'authenticate') {
    header('Content-Type: application/json');
    
    $input = json_decode(file_get_contents('php://input'), true);
    
    if (isset($input['client_secret']) && $input['client_secret'] === $oauth2_config['OAUTH2_CLIENT_SECRET']) {
        echo json_encode(array(
            'success' => true,
            'message' => 'Authentication successful',
            'access_token' => base64_encode('admin:' . $oauth2_config['OAUTH2_CLIENT_SECRET']),
            'flag' => $flag
        ));
    } else {
        http_response_code(401);
        echo json_encode(array(
            'success' => false,
            'error' => 'Invalid client credentials'
        ));
    }
    exit;
}

// Handle admin dashboard access via token
if (isset($_GET['action']) && $_GET['action'] === 'dashboard') {
    $auth_header = isset($_SERVER['HTTP_AUTHORIZATION']) ? $_SERVER['HTTP_AUTHORIZATION'] : '';
    
    if (preg_match('/Bearer\s+(.+)/', $auth_header, $matches)) {
        $token = $matches[1];
        $decoded = base64_decode($token);
        
        if ($decoded === 'admin:' . $oauth2_config['OAUTH2_CLIENT_SECRET']) {
            header('Content-Type: application/json');
            echo json_encode(array(
                'success' => true,
                'message' => 'Welcome to the admin dashboard',
                'flag' => $flag
            ));
            exit;
        }
    }
    
    http_response_code(401);
    header('Content-Type: application/json');
    echo json_encode(array(
        'success' => false,
        'error' => 'Invalid or missing authorization token'
    ));
    exit;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DBAdmin - Login</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .login-container {
            background: #ffffff;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.3);
            width: 400px;
            max-width: 90%;
        }
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo i {
            font-size: 48px;
            color: #3366CC;
        }
        .logo h1 {
            color: #333;
            font-size: 24px;
            margin-top: 10px;
        }
        .logo p {
            color: #666;
            font-size: 14px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            color: #333;
            margin-bottom: 8px;
            font-weight: 500;
        }
        .form-group input {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        .form-group input:focus {
            outline: none;
            border-color: #3366CC;
        }
        .btn {
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.3s;
            margin-bottom: 10px;
        }
        .btn-primary {
            background-color: #3366CC;
            color: white;
        }
        .btn-primary:hover {
            background-color: #2855a8;
        }
        .btn-oauth {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        .divider {
            text-align: center;
            margin: 20px 0;
            position: relative;
            color: #999;
        }
        .divider::before, .divider::after {
            content: '';
            position: absolute;
            top: 50%;
            width: 45%;
            height: 1px;
            background: #ddd;
        }
        .divider::before { left: 0; }
        .divider::after { right: 0; }
        .version {
            text-align: center;
            color: #999;
            font-size: 12px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <i class="fas fa-database"></i>
            <h1>DBAdmin</h1>
            <p>Database Administration Tool v8.11</p>
        </div>
        
        <form action="/login" method="POST" id="loginForm">
            <div class="form-group">
                <label for="email">Email Address</label>
                <input type="email" id="email" name="email" placeholder="admin@company.com" required>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" placeholder="Enter password" required>
            </div>
            <button type="submit" class="btn btn-primary">Sign In</button>
        </form>
        
        <div class="divider">or continue with</div>
        
        <button class="btn btn-oauth" style="background-color: <?php echo htmlspecialchars($oauth2_config['OAUTH2_BUTTON_COLOR']); ?>; color: white;" id="oauth-btn">
            <i class="fas <?php echo htmlspecialchars($oauth2_config['OAUTH2_ICON']); ?>"></i>
            <?php echo htmlspecialchars($oauth2_config['OAUTH2_DISPLAY_NAME']); ?>
        </button>
        
        <div class="version">Version 8.11.0</div>
    </div>

    <script>
        // Initialize application state with server configuration
        window.__DBADMIN_STATE__ = {
            appName: 'DBAdmin',
            version: '8.11.0',
            csrfToken: '<?php echo bin2hex(random_bytes(16)); ?>',
            oauth2Config: <?php echo json_encode($oauth2_config); ?>,
            endpoints: {
                login: '/login',
                authenticate: '/?action=authenticate',
                dashboard: '/?action=dashboard',
                logout: '/logout'
            }
        };

        // OAuth2 button handler
        document.getElementById('oauth-btn').addEventListener('click', function() {
            const config = window.__DBADMIN_STATE__.oauth2Config;
            // Redirect to OAuth2 authorization endpoint
            window.location.href = config.OAUTH2_AUTHORIZATION_URL + 
                '?client_id=' + encodeURIComponent(config.OAUTH2_CLIENT_ID) +
                '&scope=' + encodeURIComponent(config.OAUTH2_SCOPE) +
                '&response_type=code';
        });

        // Login form handler
        document.getElementById('loginForm').addEventListener('submit', function(e) {
            e.preventDefault();
            alert('Standard login is disabled. Please use SSO authentication.');
        });
    </script>
</body>
</html>

