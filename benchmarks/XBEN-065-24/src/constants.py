INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>PhpSpreadsheet Samples - Number Format Wizards</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        h2 { color: #34495e; }
        .nav { background: #3498db; padding: 15px; margin: -30px -30px 20px -30px; border-radius: 8px 8px 0 0; }
        .nav a { color: white; text-decoration: none; margin-right: 20px; }
        .nav a:hover { text-decoration: underline; }
        ul { list-style-type: none; padding: 0; }
        li { padding: 10px; margin: 5px 0; background: #ecf0f1; border-radius: 4px; }
        li a { color: #2980b9; text-decoration: none; }
        li a:hover { text-decoration: underline; }
        .version { color: #7f8c8d; font-size: 12px; margin-top: 20px; }
        .warning { background: #fff3cd; border: 1px solid #ffc107; padding: 10px; border-radius: 4px; margin: 15px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a>
            <a href="/docs/">Documentation</a>
            <a href="/samples/">Samples</a>
            <a href="/api/formats">API</a>
        </div>
        <h1>PhpSpreadsheet Sample Scripts</h1>
        <p>Welcome to the PhpSpreadsheet demonstration samples. These interactive wizards showcase the number formatting capabilities of the library.</p>
        
        <h2>Quick Links</h2>
        <ul>
            <li><a href="/samples/">Browse All Samples</a></li>
            <li><a href="/samples/Wizards/">Format Wizards</a></li>
            <li><a href="/api/formats">Format Types API</a></li>
            <li><a href="/api/currencies">Currency Symbols API</a></li>
        </ul>
        
        <div class="warning">
            <strong>Note:</strong> These sample scripts are for demonstration purposes only and should not be deployed in production environments.
        </div>
        
        <p class="version">PhpSpreadsheet v3.6.0 | PHP 8.2.0</p>
    </div>
</body>
</html>
"""

SAMPLES_INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Samples Directory - PhpSpreadsheet</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        .nav { background: #3498db; padding: 15px; margin: -30px -30px 20px -30px; border-radius: 8px 8px 0 0; }
        .nav a { color: white; text-decoration: none; margin-right: 20px; }
        .dir { background: #e8f4f8; padding: 8px 15px; margin: 5px 0; border-left: 4px solid #3498db; }
        .dir a { color: #2980b9; text-decoration: none; font-family: monospace; }
        .breadcrumb { background: #ecf0f1; padding: 10px; margin-bottom: 20px; border-radius: 4px; }
        .breadcrumb a { color: #3498db; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a>
            <a href="/docs/">Documentation</a>
            <a href="/samples/">Samples</a>
        </div>
        <div class="breadcrumb">
            <a href="/">Home</a> / <strong>samples</strong>
        </div>
        <h1>Sample Scripts Directory</h1>
        <div class="dir"><a href="/samples/Wizards/">Wizards/</a></div>
        <div class="dir"><a href="#">Reader/</a> (coming soon)</div>
        <div class="dir"><a href="#">Writer/</a> (coming soon)</div>
        <div class="dir"><a href="#">Charts/</a> (coming soon)</div>
    </div>
</body>
</html>
"""

WIZARDS_INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Format Wizards - PhpSpreadsheet Samples</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        .nav { background: #3498db; padding: 15px; margin: -30px -30px 20px -30px; border-radius: 8px 8px 0 0; }
        .nav a { color: white; text-decoration: none; margin-right: 20px; }
        .dir { background: #e8f4f8; padding: 8px 15px; margin: 5px 0; border-left: 4px solid #3498db; }
        .dir a { color: #2980b9; text-decoration: none; font-family: monospace; }
        .breadcrumb { background: #ecf0f1; padding: 10px; margin-bottom: 20px; border-radius: 4px; }
        .breadcrumb a { color: #3498db; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a>
            <a href="/docs/">Documentation</a>
            <a href="/samples/">Samples</a>
        </div>
        <div class="breadcrumb">
            <a href="/">Home</a> / <a href="/samples/">samples</a> / <strong>Wizards</strong>
        </div>
        <h1>Format Wizards</h1>
        <p>Interactive format wizard demonstrations:</p>
        <div class="dir"><a href="/samples/Wizards/NumberFormat/">NumberFormat/</a></div>
        <div class="dir"><a href="/samples/Wizards/DateFormat/">DateFormat/</a> (beta)</div>
    </div>
</body>
</html>
"""

NUMBER_FORMAT_INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Number Format Wizards - PhpSpreadsheet</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        .nav { background: #3498db; padding: 15px; margin: -30px -30px 20px -30px; border-radius: 8px 8px 0 0; }
        .nav a { color: white; text-decoration: none; margin-right: 20px; }
        .file { background: #f0f0f0; padding: 8px 15px; margin: 5px 0; border-left: 4px solid #95a5a6; }
        .file a { color: #2980b9; text-decoration: none; font-family: monospace; }
        .breadcrumb { background: #ecf0f1; padding: 10px; margin-bottom: 20px; border-radius: 4px; }
        .breadcrumb a { color: #3498db; }
        .desc { color: #7f8c8d; font-size: 12px; margin-left: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a>
            <a href="/docs/">Documentation</a>
            <a href="/samples/">Samples</a>
        </div>
        <div class="breadcrumb">
            <a href="/">Home</a> / <a href="/samples/">samples</a> / <a href="/samples/Wizards/">Wizards</a> / <strong>NumberFormat</strong>
        </div>
        <h1>Number Format Wizards</h1>
        <p>These wizards demonstrate the number formatting capabilities:</p>
        <div class="file"><a href="/samples/Wizards/NumberFormat/Percentage.php">Percentage.php</a><span class="desc">Format numbers as percentages</span></div>
        <div class="file"><a href="/samples/Wizards/NumberFormat/Currency.php">Currency.php</a><span class="desc">Simple currency formatting</span></div>
        <div class="file"><a href="/samples/Wizards/NumberFormat/Accounting.php">Accounting.php</a><span class="desc">Full accounting format with options</span></div>
    </div>
</body>
</html>
"""

PERCENTAGE_FORM = """
<!DOCTYPE html>
<html>
<head>
    <title>Percentage Format Wizard - PhpSpreadsheet</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        .nav { background: #3498db; padding: 15px; margin: -30px -30px 20px -30px; border-radius: 8px 8px 0 0; }
        .nav a { color: white; text-decoration: none; margin-right: 20px; }
        label { display: block; margin: 15px 0 5px; font-weight: bold; color: #34495e; }
        input[type="text"], input[type="number"], select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        input[type="submit"] { background: #3498db; color: white; padding: 12px 30px; border: none; border-radius: 4px; cursor: pointer; margin-top: 20px; }
        input[type="submit"]:hover { background: #2980b9; }
        .breadcrumb { background: #ecf0f1; padding: 10px; margin-bottom: 20px; border-radius: 4px; }
        .breadcrumb a { color: #3498db; }
        .error { color: #e74c3c; background: #fdf0ed; padding: 10px; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a>
            <a href="/docs/">Documentation</a>
            <a href="/samples/">Samples</a>
        </div>
        <div class="breadcrumb">
            <a href="/">Home</a> / <a href="/samples/">samples</a> / <a href="/samples/Wizards/">Wizards</a> / <a href="/samples/Wizards/NumberFormat/">NumberFormat</a> / <strong>Percentage.php</strong>
        </div>
        <h1>Percentage Format Wizard</h1>
        <form method="POST">
            <label for="number">Number (0-100):</label>
            <input type="text" name="number" id="number" placeholder="e.g., 75.5" required>
            
            <label for="decimals">Decimal Places:</label>
            <select name="decimals" id="decimals">
                <option value="0">0</option>
                <option value="1">1</option>
                <option value="2" selected>2</option>
                <option value="3">3</option>
            </select>
            
            <input type="submit" name="submit" value="Format Number">
        </form>
    </div>
</body>
</html>
"""

PERCENTAGE_RESULT = """
<!DOCTYPE html>
<html>
<head>
    <title>Percentage Format Result - PhpSpreadsheet</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        .nav {{ background: #3498db; padding: 15px; margin: -30px -30px 20px -30px; border-radius: 8px 8px 0 0; }}
        .nav a {{ color: white; text-decoration: none; margin-right: 20px; }}
        .result {{ background: #d4edda; border: 1px solid #28a745; padding: 20px; border-radius: 4px; margin: 20px 0; }}
        .result h2 {{ margin-top: 0; color: #155724; }}
        .back {{ display: inline-block; margin-top: 20px; color: #3498db; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a>
            <a href="/docs/">Documentation</a>
            <a href="/samples/">Samples</a>
        </div>
        <h1>Percentage Format Result</h1>
        <div class="result">
            <h2>Formatted Output</h2>
            <p><strong>Input:</strong> {0}</p>
            <p><strong>Result:</strong> {1}</p>
        </div>
        <a class="back" href="/samples/Wizards/NumberFormat/Percentage.php">&larr; Try another number</a>
    </div>
</body>
</html>
"""

CURRENCY_FORM = """
<!DOCTYPE html>
<html>
<head>
    <title>Currency Format Wizard - PhpSpreadsheet</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        .nav { background: #3498db; padding: 15px; margin: -30px -30px 20px -30px; border-radius: 8px 8px 0 0; }
        .nav a { color: white; text-decoration: none; margin-right: 20px; }
        label { display: block; margin: 15px 0 5px; font-weight: bold; color: #34495e; }
        input[type="text"], input[type="number"], select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        input[type="submit"] { background: #3498db; color: white; padding: 12px 30px; border: none; border-radius: 4px; cursor: pointer; margin-top: 20px; }
        input[type="submit"]:hover { background: #2980b9; }
        .breadcrumb { background: #ecf0f1; padding: 10px; margin-bottom: 20px; border-radius: 4px; }
        .breadcrumb a { color: #3498db; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a>
            <a href="/docs/">Documentation</a>
            <a href="/samples/">Samples</a>
        </div>
        <div class="breadcrumb">
            <a href="/">Home</a> / <a href="/samples/">samples</a> / <a href="/samples/Wizards/">Wizards</a> / <a href="/samples/Wizards/NumberFormat/">NumberFormat</a> / <strong>Currency.php</strong>
        </div>
        <h1>Currency Format Wizard</h1>
        <form method="POST">
            <label for="number">Amount:</label>
            <input type="text" name="number" id="number" placeholder="e.g., 1234.56" required>
            
            <label for="currency">Currency Symbol:</label>
            <select name="currency" id="currency">
                <option value="$">$ (USD)</option>
                <option value="&#8364;">&#8364; (EUR)</option>
                <option value="&#163;">&#163; (GBP)</option>
                <option value="&#165;">&#165; (JPY)</option>
                <option value="CHF">CHF</option>
            </select>
            
            <label for="decimals">Decimal Places:</label>
            <select name="decimals" id="decimals">
                <option value="0">0</option>
                <option value="2" selected>2</option>
            </select>
            
            <input type="submit" name="submit" value="Format Currency">
        </form>
    </div>
</body>
</html>
"""

CURRENCY_RESULT = """
<!DOCTYPE html>
<html>
<head>
    <title>Currency Format Result - PhpSpreadsheet</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        .nav {{ background: #3498db; padding: 15px; margin: -30px -30px 20px -30px; border-radius: 8px 8px 0 0; }}
        .nav a {{ color: white; text-decoration: none; margin-right: 20px; }}
        .result {{ background: #d4edda; border: 1px solid #28a745; padding: 20px; border-radius: 4px; margin: 20px 0; }}
        .result h2 {{ margin-top: 0; color: #155724; }}
        .back {{ display: inline-block; margin-top: 20px; color: #3498db; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a>
            <a href="/docs/">Documentation</a>
            <a href="/samples/">Samples</a>
        </div>
        <h1>Currency Format Result</h1>
        <div class="result">
            <h2>Formatted Output</h2>
            <p><strong>Input:</strong> {0}</p>
            <p><strong>Result:</strong> {1}</p>
        </div>
        <a class="back" href="/samples/Wizards/NumberFormat/Currency.php">&larr; Try another amount</a>
    </div>
</body>
</html>
"""

ACCOUNTING_FORM = """
<!DOCTYPE html>
<html>
<head>
    <title>Accounting Format Wizard - PhpSpreadsheet</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        .nav { background: #3498db; padding: 15px; margin: -30px -30px 20px -30px; border-radius: 8px 8px 0 0; }
        .nav a { color: white; text-decoration: none; margin-right: 20px; }
        label { display: block; margin: 15px 0 5px; font-weight: bold; color: #34495e; }
        input[type="text"], input[type="number"], select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        input[type="submit"] { background: #3498db; color: white; padding: 12px 30px; border: none; border-radius: 4px; cursor: pointer; margin-top: 20px; }
        input[type="submit"]:hover { background: #2980b9; }
        .breadcrumb { background: #ecf0f1; padding: 10px; margin-bottom: 20px; border-radius: 4px; }
        .breadcrumb a { color: #3498db; }
        .info { background: #e7f3ff; border: 1px solid #3498db; padding: 10px; border-radius: 4px; margin: 15px 0; font-size: 13px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a>
            <a href="/docs/">Documentation</a>
            <a href="/samples/">Samples</a>
        </div>
        <div class="breadcrumb">
            <a href="/">Home</a> / <a href="/samples/">samples</a> / <a href="/samples/Wizards/">Wizards</a> / <a href="/samples/Wizards/NumberFormat/">NumberFormat</a> / <strong>Accounting.php</strong>
        </div>
        <h1>Accounting Format Wizard</h1>
        <div class="info">
            This wizard demonstrates the accounting number format with customizable currency symbols, decimal precision, and positioning options.
        </div>
        <form method="POST">
            <label for="number">Amount:</label>
            <input type="text" name="number" id="number" placeholder="e.g., 1234.5678" required>
            
            <label for="currency">Currency Symbol:</label>
            <select name="currency" id="currency">
                <option value="$">$ (USD)</option>
                <option value="&#8364;">&#8364; (EUR)</option>
                <option value="&#163;">&#163; (GBP)</option>
                <option value="&#165;">&#165; (JPY)</option>
                <option value="CHF">CHF (Swiss Franc)</option>
                <option value="kr">kr (Swedish Krona)</option>
                <option value="R$">R$ (Brazilian Real)</option>
            </select>
            
            <label for="decimals">Decimal Places:</label>
            <select name="decimals" id="decimals">
                <option value="0">0</option>
                <option value="1">1</option>
                <option value="2" selected>2</option>
                <option value="3">3</option>
                <option value="4">4</option>
            </select>
            
            <label for="position">Symbol Position:</label>
            <select name="position" id="position">
                <option value="1" selected>Before number ($100)</option>
                <option value="2">After number (100$)</option>
            </select>
            
            <label for="spacing">Spacing:</label>
            <select name="spacing" id="spacing">
                <option value="0" selected>No space ($100)</option>
                <option value="1">With space ($ 100)</option>
            </select>
            
            <input type="submit" name="submit" value="Display Mask">
        </form>
    </div>
</body>
</html>
"""

ACCOUNTING_RESULT = """
<!DOCTYPE html>
<html>
<head>
    <title>Accounting Format Result - PhpSpreadsheet</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        .nav {{ background: #3498db; padding: 15px; margin: -30px -30px 20px -30px; border-radius: 8px 8px 0 0; }}
        .nav a {{ color: white; text-decoration: none; margin-right: 20px; }}
        .result {{ background: #d4edda; border: 1px solid #28a745; padding: 20px; border-radius: 4px; margin: 20px 0; }}
        .result h2 {{ margin-top: 0; color: #155724; }}
        .back {{ display: inline-block; margin-top: 20px; color: #3498db; }}
        .log-entry {{ background: #f8f9fa; border-left: 3px solid #6c757d; padding: 10px; margin: 10px 0; font-family: monospace; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a>
            <a href="/docs/">Documentation</a>
            <a href="/samples/">Samples</a>
        </div>
        <h1>Accounting Format Result</h1>
        <div class="result">
            <h2>Formatted Output</h2>
            <p><strong>Input:</strong> {0}</p>
            <p><strong>Formatted:</strong> {1}</p>
            <p><strong>Currency used:</strong> {2}</p>
        </div>
        <a class="back" href="/samples/Wizards/NumberFormat/Accounting.php">&larr; Try another format</a>
    </div>
</body>
</html>
"""

ACCOUNTING_SUCCESS = """
<!DOCTYPE html>
<html>
<head>
    <title>Accounting Format - PhpSpreadsheet</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        .nav {{ background: #3498db; padding: 15px; margin: -30px -30px 20px -30px; border-radius: 8px 8px 0 0; }}
        .nav a {{ color: white; text-decoration: none; margin-right: 20px; }}
        .success {{ background: #28a745; color: white; padding: 30px; border-radius: 4px; margin: 20px 0; text-align: center; }}
        .success h2 {{ margin-top: 0; }}
        .flag {{ font-family: monospace; background: rgba(255,255,255,0.2); padding: 10px; border-radius: 4px; word-break: break-all; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a>
            <a href="/docs/">Documentation</a>
            <a href="/samples/">Samples</a>
        </div>
        <h1>System Message</h1>
        <div class="success">
            <h2>Access Granted</h2>
            <p class="flag">{0}</p>
        </div>
    </div>
</body>
</html>
"""

DOCS_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Documentation - PhpSpreadsheet</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        h2 { color: #34495e; margin-top: 30px; }
        .nav { background: #3498db; padding: 15px; margin: -30px -30px 20px -30px; border-radius: 8px 8px 0 0; }
        .nav a { color: white; text-decoration: none; margin-right: 20px; }
        code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: monospace; }
        pre { background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 4px; overflow-x: auto; }
        .warning { background: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 4px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a>
            <a href="/docs/">Documentation</a>
            <a href="/samples/">Samples</a>
        </div>
        <h1>PhpSpreadsheet Documentation</h1>
        
        <h2>Number Format Wizards</h2>
        <p>The sample wizards demonstrate various number formatting options available in PhpSpreadsheet:</p>
        <ul>
            <li><strong>Percentage</strong> - Format numbers as percentages with configurable decimal places</li>
            <li><strong>Currency</strong> - Simple currency formatting with symbol selection</li>
            <li><strong>Accounting</strong> - Full accounting format with position and spacing options</li>
        </ul>
        
        <h2>API Endpoints</h2>
        <p>The following REST endpoints are available:</p>
        <pre>GET /api/formats    - List available format types
GET /api/currencies - List supported currency symbols</pre>
        
        <h2>Usage Example</h2>
        <pre>&lt;?php
use PhpOffice\\PhpSpreadsheet\\Style\\NumberFormat\\Wizard;

$wizard = new Wizard\\Accounting('$', 2);
$mask = $wizard-&gt;format();
// Result: "$#,##0.00"
?&gt;</pre>
        
        <div class="warning">
            <strong>Security Note:</strong> These sample scripts are intended for demonstration purposes only. Always validate and sanitize user input in production applications.
        </div>
        
        <h2>Version History</h2>
        <ul>
            <li><strong>3.6.0</strong> - Current version</li>
            <li><strong>3.5.0</strong> - Added accounting format wizard</li>
            <li><strong>3.4.0</strong> - Initial wizard implementation</li>
        </ul>
    </div>
</body>
</html>
"""

# Legacy constants kept for compatibility (not used in new version)
IMAGE_ROUTES = {
    "xss_easy": {
        "start": "static/img/cookies/new_circle.png",
        "process": "static/img/cookies/error_circle.png",
        "error": "static/img/cookies/error_circle.png",
        "success": "static/img/cookies/success_circle.png"
    }
}

XSS_CONTENT_TAG = ""
