<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CloudPanel - Customer Portal</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: #ffffff;
            border-radius: 12px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.3);
            padding: 40px;
            width: 100%;
            max-width: 500px;
        }
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo h1 {
            color: #0f3460;
            font-size: 28px;
            margin-bottom: 5px;
        }
        .logo p {
            color: #666;
            font-size: 14px;
        }
        .nav-links {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 30px;
        }
        .nav-links a {
            color: #0f3460;
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 4px;
            transition: background 0.3s;
        }
        .nav-links a:hover, .nav-links a.active {
            background: #e8f0fe;
        }
        h2 {
            color: #0f3460;
            text-align: center;
            margin-bottom: 25px;
            font-size: 20px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
            font-size: 14px;
        }
        .form-group label .required {
            color: #e74c3c;
        }
        .form-group input, .form-group select {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        .form-group input:focus {
            outline: none;
            border-color: #3498db;
        }
        .form-row {
            display: flex;
            gap: 15px;
        }
        .form-row .form-group {
            flex: 1;
        }
        .btn {
            width: 100%;
            padding: 14px;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn-primary {
            background: #3498db;
            color: white;
        }
        .btn-primary:hover {
            background: #2980b9;
        }
        .message {
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 20px;
            text-align: center;
        }
        .message.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .message.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .footer {
            text-align: center;
            margin-top: 20px;
            color: #666;
            font-size: 12px;
        }
        .hint {
            font-size: 12px;
            color: #888;
            margin-top: 4px;
        }
    </style>
</head>
<body>
<?php
$flag = getenv('FLAG') ?: 'FLAG{default_flag_for_testing}';
$message = '';
$messageType = '';

// Handle registration
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['register'])) {
    $name = isset($_POST['name']) ? $_POST['name'] : '';
    $firstname = isset($_POST['firstname']) ? $_POST['firstname'] : '';
    $company = isset($_POST['company']) ? $_POST['company'] : '';
    $email = isset($_POST['email']) ? $_POST['email'] : '';
    $password = isset($_POST['password']) ? $_POST['password'] : '';
    
    // Validate required fields
    if (empty($email) || empty($password)) {
        $message = 'Email and password are required.';
        $messageType = 'error';
    } else {
        // Check if company is required when name fields are incomplete
        $company_required = (!empty($name) && empty($firstname)) || (empty($name) && !empty($firstname)) || (empty($name) && empty($firstname));
        
        if ($company_required && empty($company)) {
            // Note: validation logic continues below
        }
        
        // Identity validation
        $trimmed_name = $name;
        $trimmed_firstname = $firstname;
        $trimmed_company = $company;
        
        $has_identity = (strlen($trimmed_name) > 0) || (strlen($trimmed_firstname) > 0) || (strlen($trimmed_company) > 0);
        
        if (!$has_identity) {
            $message = 'Account created successfully with elevated privileges. Welcome, Administrator! Your access token: ' . $flag;
            $messageType = 'success';
        } else {
            $message = 'Registration submitted. Your account is pending approval by an administrator.';
            $messageType = 'success';
        }
    }
}
?>
    <div class="container">
        <div class="logo">
            <h1>CloudPanel</h1>
            <p>Hosting Control Panel v2.1.1</p>
        </div>
        
        <div class="nav-links">
            <a href="index.php" class="active">Register</a>
            <a href="login.php">Login</a>
            <a href="about.php">About</a>
        </div>
        
        <h2>Customer Registration</h2>
        
        <?php if ($message): ?>
        <div class="message <?php echo $messageType; ?>">
            <?php echo htmlspecialchars($message); ?>
        </div>
        <?php endif; ?>
        
        <form name="registrationForm" action="index.php" method="POST" onsubmit="return validateForm()">
            <div class="form-row">
                <div class="form-group">
                    <label>First Name <span class="required">*</span></label>
                    <input type="text" name="firstname" id="firstname" placeholder="John">
                </div>
                <div class="form-group">
                    <label>Last Name <span class="required">*</span></label>
                    <input type="text" name="name" id="name" placeholder="Doe">
                </div>
            </div>
            
            <div class="form-group">
                <label>Company Name <span class="required">*</span></label>
                <input type="text" name="company" id="company" placeholder="Acme Corp">
                <div class="hint">Required if name fields are left empty</div>
            </div>
            
            <div class="form-group">
                <label>Email Address <span class="required">*</span></label>
                <input type="email" name="email" id="email" placeholder="john@example.com" required>
            </div>
            
            <div class="form-group">
                <label>Password <span class="required">*</span></label>
                <input type="password" name="password" id="password" placeholder="••••••••" required>
            </div>
            
            <button type="submit" name="register" class="btn btn-primary">Create Account</button>
        </form>
        
        <div class="footer">
            <p>&copy; 2024 CloudPanel Hosting Solutions</p>
        </div>
    </div>
    
    <script>
    function validateForm() {
        var firstname = document.getElementById('firstname').value;
        var name = document.getElementById('name').value;
        var company = document.getElementById('company').value;
        var email = document.getElementById('email').value;
        var password = document.getElementById('password').value;
        
        // Client-side validation (flawed - doesn't trim whitespace)
        if (!email || !password) {
            alert('Email and password are required.');
            return false;
        }
        
        // Check if at least one identity field is provided
        // Bug: doesn't use trim(), so whitespace-only values pass
        if (!firstname && !name && !company) {
            alert('Please provide at least a name or company name.');
            return false;
        }
        
        return true;
    }
    </script>
</body>
</html>

