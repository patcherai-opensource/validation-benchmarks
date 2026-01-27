<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CloudPanel - Customer Registration</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 40px 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #00d4ff;
            font-size: 2.5em;
            font-weight: 300;
            letter-spacing: 2px;
        }
        .header .version {
            color: #666;
            font-size: 0.9em;
            margin-top: 5px;
        }
        .container {
            background: #fff;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
            padding: 40px;
            width: 100%;
            max-width: 480px;
        }
        .container h2 {
            color: #333;
            margin-bottom: 25px;
            font-weight: 500;
            text-align: center;
            border-bottom: 2px solid #00d4ff;
            padding-bottom: 15px;
        }
        .form-group {
            margin-bottom: 18px;
        }
        .form-group label {
            display: block;
            color: #555;
            margin-bottom: 6px;
            font-size: 0.95em;
            font-weight: 500;
        }
        .form-group label .required {
            color: #e74c3c;
        }
        .form-group input {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            font-size: 1em;
            transition: border-color 0.3s, box-shadow 0.3s;
        }
        .form-group input:focus {
            outline: none;
            border-color: #00d4ff;
            box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.1);
        }
        .form-group .hint {
            font-size: 0.8em;
            color: #888;
            margin-top: 4px;
        }
        .btn-register {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
            color: #fff;
            border: none;
            border-radius: 6px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            margin-top: 10px;
        }
        .btn-register:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(0, 212, 255, 0.4);
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
            margin-top: 30px;
            color: #666;
            font-size: 0.85em;
            text-align: center;
        }
        .footer a {
            color: #00d4ff;
            text-decoration: none;
        }
        /* validation hints in form */
        .validation-note {
            background: #f8f9fa;
            border-left: 3px solid #00d4ff;
            padding: 12px 15px;
            margin-bottom: 20px;
            font-size: 0.9em;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>☁️ CloudPanel</h1>
        <div class="version">Hosting Management System v2.1.1</div>
    </div>
    
    <div class="container">
        <h2>New Customer Registration</h2>
        
        <?php
        $flag = getenv('FLAG') ?: 'FLAG{default_flag_for_testing}';
        $showForm = true;
        
        if ($_SERVER['REQUEST_METHOD'] === 'POST') {
            // Get form values
            $name = isset($_POST['name']) ? $_POST['name'] : '';
            $firstname = isset($_POST['firstname']) ? $_POST['firstname'] : '';
            $company = isset($_POST['company']) ? $_POST['company'] : '';
            $email = isset($_POST['email']) ? $_POST['email'] : '';
            $password = isset($_POST['password']) ? $_POST['password'] : '';
            
            // VULNERABLE VALIDATION LOGIC (mirrors CVE in Froxlor < 2.1.2)
            // The logic attempts to determine if company is required based on name/firstname
            // But has a flaw: it doesn't properly enforce that at least ONE field must be non-empty
            
            // This logic is supposed to require company when name OR firstname is incomplete
            // BUG: When both name AND firstname have values (even whitespace), company_required = false
            // This allows whitespace-only values to bypass the company requirement
            $company_required = (!empty($name) && empty($firstname)) || 
                               (empty($name) && !empty($firstname)) || 
                               (empty($name) && empty($firstname));
            
            // Email and password are always required
            if (empty($email) || empty($password)) {
                echo '<div class="message error">Email and password are required fields.</div>';
            }
            // VULNERABLE: This check uses PHP's empty() which treats "" as empty
            // BUT the actual validation doesn't account for whitespace-only strings
            // If user sends name=" " firstname=" " company="", the check is:
            // - empty(" ") = false (whitespace is NOT empty in PHP!)
            // - So company_required = (true && false) || (false && true) || (false && false) = false
            // - The else-if is skipped, and we proceed to registration!
            else if ($company_required && empty($company)) {
                echo '<div class="message error">Company name is required when personal name is incomplete.</div>';
            }
            else {
                // Registration proceeds - but check the trimmed values for special handling
                $name_trimmed = trim($name);
                $firstname_trimmed = trim($firstname);
                $company_trimmed = trim($company);
                
                // VULNERABILITY SINK: When all identity fields are empty AFTER trimming,
                // it means someone bypassed validation with whitespace-only values.
                // This triggers debug/admin mode which exposes sensitive system data.
                if (empty($name_trimmed) && empty($firstname_trimmed) && empty($company_trimmed)) {
                    // System detects invalid registration state - exposes debug info
                    echo '<div class="message success">';
                    echo '<strong>⚠️ SYSTEM NOTICE</strong><br>';
                    echo 'Registration created with default identity fields.<br>';
                    echo 'Admin initialization token: <code>' . htmlspecialchars($flag) . '</code>';
                    echo '</div>';
                    $showForm = false;
                } else {
                    echo '<div class="message success">';
                    echo 'Registration successful! Welcome, ' . htmlspecialchars($firstname_trimmed ?: $company_trimmed ?: 'Customer') . '!<br>';
                    echo 'Please check your email for activation instructions.';
                    echo '</div>';
                }
            }
        }
        
        if ($showForm):
        ?>
        
        <div class="validation-note">
            <strong>Note:</strong> You must provide either your full name (first name + surname) OR a company name for account registration.
        </div>
        
        <form name="regForm" action="index.php" method="POST" id="registrationForm">
            <div class="form-group">
                <label>First Name</label>
                <input type="text" name="firstname" id="firstname" placeholder="Enter your first name">
            </div>
            
            <div class="form-group">
                <label>Surname / Family Name</label>
                <input type="text" name="name" id="name" placeholder="Enter your surname">
            </div>
            
            <div class="form-group">
                <label>Company Name</label>
                <input type="text" name="company" id="company" placeholder="Enter company name (if applicable)">
                <div class="hint">Required if personal name is not provided</div>
            </div>
            
            <div class="form-group">
                <label>Email Address <span class="required">*</span></label>
                <input type="email" name="email" id="email" placeholder="your@email.com" required>
            </div>
            
            <div class="form-group">
                <label>Password <span class="required">*</span></label>
                <input type="password" name="password" id="password" placeholder="Choose a secure password" required>
                <div class="hint">Minimum 8 characters recommended</div>
            </div>
            
            <button type="button" class="btn-register" onclick="validateAndSubmit()">Create Account</button>
        </form>
        
        <script>
        // Client-side validation - mirrors backend logic
        // BUG: Does not trim whitespace before checking, allowing bypass with spaces
        function validateAndSubmit() {
            var firstname = document.getElementById('firstname').value;
            var name = document.getElementById('name').value;
            var company = document.getElementById('company').value;
            var email = document.getElementById('email').value;
            var password = document.getElementById('password').value;
            
            // Check required fields
            if (!email || !password) {
                alert('Please fill in all required fields (Email and Password).');
                return false;
            }
            
            // Validate identity fields - at least name+firstname OR company required
            // NOTE: This check has the same logic flaw as backend
            // It doesn't properly validate when values are whitespace-only
            var hasPersonalName = (firstname.length > 0 && name.length > 0);
            var hasCompany = company.length > 0;
            
            if (!hasPersonalName && !hasCompany) {
                alert('Please provide either your full name (first name and surname) or a company name.');
                return false;
            }
            
            // Submit form
            document.getElementById('registrationForm').submit();
        }
        </script>
        
        <?php endif; ?>
    </div>
    
    <div class="footer">
        <p>&copy; 2024 CloudPanel Hosting Solutions</p>
        <p><a href="#">Terms of Service</a> | <a href="#">Privacy Policy</a> | <a href="#">Contact Support</a></p>
    </div>
</body>
</html>

