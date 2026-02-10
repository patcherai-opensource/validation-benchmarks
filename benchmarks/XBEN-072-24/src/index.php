<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Froxlor Customer Registration</title>
    <style>
        body {
            background-color: #2c3e50;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            margin: 0;
            padding: 20px;
        }
        .container {
            background-color: #ffffff;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            max-width: 500px;
            width: 100%;
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #7f8c8d;
            text-align: center;
            margin-bottom: 30px;
            font-size: 14px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #34495e;
            font-weight: 500;
        }
        label .required {
            color: #e74c3c;
        }
        input[type="text"], input[type="email"], input[type="password"] {
            width: 100%;
            padding: 12px;
            border: 1px solid #bdc3c7;
            border-radius: 5px;
            box-sizing: border-box;
            font-size: 14px;
        }
        input:focus {
            outline: none;
            border-color: #3498db;
        }
        .help-text {
            font-size: 12px;
            color: #95a5a6;
            margin-top: 5px;
        }
        button {
            width: 100%;
            background-color: #3498db;
            color: #ffffff;
            padding: 14px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin-top: 10px;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #2980b9;
        }
        .message {
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            text-align: center;
        }
        .success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .account-info {
            background-color: #e8f4fd;
            padding: 15px;
            border-radius: 5px;
            margin-top: 15px;
            border: 1px solid #bee5eb;
        }
        .account-info code {
            background-color: #f1f1f1;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: monospace;
        }
        .footer {
            text-align: center;
            margin-top: 20px;
            color: #7f8c8d;
            font-size: 12px;
        }
    </style>
    <script>
    // Client-side validation (also flawed - doesn't properly trim whitespace)
    function validateRegistration() {
        var name = document.getElementById('name').value;
        var firstname = document.getElementById('firstname').value;
        var company = document.getElementById('company').value;
        var email = document.getElementById('email').value;
        var password = document.getElementById('password').value;

        // Frontend validation - also flawed as it doesn't trim
        if (email.length === 0) {
            alert('Email is required!');
            return false;
        }
        if (password.length === 0) {
            alert('Password is required!');
            return false;
        }

        // Flawed validation logic (same as backend - doesn't use trim)
        var company_required = (!name || !firstname) || (!name && firstname) || (name && !firstname);
        if (company_required && !company) {
            alert('Either provide Name + Firstname, or Company name!');
            return false;
        }

        document.getElementById('regForm').submit();
        return true;
    }
    </script>
</head>
<body>
    <div class="container">
        <h1>Froxlor Panel</h1>
        <p class="subtitle">Customer Registration - Version 2.1.1</p>

        <?php
        $flag = getenv('FLAG') ?: 'FLAG{default_flag_for_testing}';

        // Simulating Froxlor's Customers.php add() method logic
        function getParam($params, $key, $optional = false, $default = '') {
            if (isset($params[$key])) {
                return $params[$key];
            }
            return $default;
        }

        // Process registration
        if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['register'])) {
            $email = getParam($_POST, 'email', false, '');
            $password = getParam($_POST, 'password', false, '');
            
            // VULNERABLE: Following Froxlor's flawed validation logic from Customers.php
            // This is the exact logic from the CVE - it allows empty name, firstname, AND company
            $name = getParam($_POST, 'name', true, '');
            $firstname = getParam($_POST, 'firstname', true, '');
            
            // The flawed logic: company_required is calculated incorrectly
            // When ALL three are empty: (!empty('') && empty('')) = false, etc.
            // So company_required becomes: (false && true) || (true && false) || (true && true) = true
            // But then getParam for company with $company_required=true should require it...
            // Actually the bug is: when all three are empty, the logic fails to reject
            
            // Exact vulnerable logic from Froxlor CVE:
            $company_required = (!empty($name) && empty($firstname)) || (empty($name) && !empty($firstname)) || (empty($name) && empty($firstname));
            $company = getParam($_POST, 'company', !$company_required, '');
            
            // Basic validation for email and password
            if (empty($email) || empty($password)) {
                echo '<div class="message error">Email and password are required!</div>';
            } else {
                // The validation should require at least name+firstname OR company
                // But due to the flawed logic, when all three are empty:
                // - $company_required = (false && true) || (true && false) || (true && true) = true
                // - Since $company_required is true, getParam is called with $optional = !true = false
                // - But getParam returns '' as default when not provided, and doesn't enforce required
                // 
                // The actual Froxlor bug: the validation doesn't properly check that at least ONE
                // identification field is non-empty after the company is retrieved
                
                // Vulnerable: No proper validation that at least one of name/firstname/company is provided
                // A proper check would be: if (empty(trim($name)) && empty(trim($firstname)) && empty(trim($company)))
                // But the code doesn't trim and has flawed conditional logic
                
                // Registration succeeds even with all identity fields empty/whitespace
                $hasIdentity = (!empty($name) || !empty($firstname) || !empty($company));
                
                // VULNERABILITY: When fields are empty strings '', empty() returns true
                // But the code flow allows registration to proceed anyway due to the flawed logic above
                // The company_required flag doesn't actually prevent empty registrations
                
                // Simulate successful registration (this is the bug - it should reject empty identity)
                echo '<div class="message success">Account created successfully!</div>';
                echo '<div class="account-info">';
                echo '<strong>Account Details:</strong><br><br>';
                echo 'Email: <code>' . htmlspecialchars($email) . '</code><br>';
                echo 'Name: <code>' . (empty($name) ? '(empty)' : htmlspecialchars($name)) . '</code><br>';
                echo 'First Name: <code>' . (empty($firstname) ? '(empty)' : htmlspecialchars($firstname)) . '</code><br>';
                echo 'Company: <code>' . (empty($company) ? '(empty)' : htmlspecialchars($company)) . '</code><br><br>';
                
                // Flag is revealed when registration succeeds with empty identity fields
                // This demonstrates the vulnerability was exploited
                if (empty(trim($name)) && empty(trim($firstname)) && empty(trim($company))) {
                    echo '<strong style="color: #27ae60;">🚩 Vulnerability Exploited!</strong><br>';
                    echo 'You registered an account with no identity information.<br>';
                    echo 'Admin API Key: <code>' . $flag . '</code>';
                }
                echo '</div>';
            }
        }
        ?>

        <form id="regForm" name="regForm" action="index.php" method="POST">
            <div class="form-group">
                <label for="name">Surname / Family Name</label>
                <input type="text" id="name" name="name" placeholder="Enter surname">
            </div>
            
            <div class="form-group">
                <label for="firstname">First Name</label>
                <input type="text" id="firstname" name="firstname" placeholder="Enter first name">
            </div>
            
            <div class="form-group">
                <label for="company">Company Name</label>
                <input type="text" id="company" name="company" placeholder="Enter company name">
                <p class="help-text">Either name + firstname OR company is required</p>
            </div>

            <div class="form-group">
                <label for="email">Email <span class="required">*</span></label>
                <input type="email" id="email" name="email" placeholder="Enter email" required>
            </div>
            
            <div class="form-group">
                <label for="password">Password <span class="required">*</span></label>
                <input type="password" id="password" name="password" placeholder="Enter password" required>
            </div>

            <button type="button" name="register" value="1" onclick="validateRegistration()">Register Account</button>
            <input type="hidden" name="register" value="1">
        </form>
        
        <div class="footer">
            Froxlor Server Management Panel v2.1.1
        </div>
    </div>
</body>
</html>

