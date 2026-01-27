INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>PhpSpreadsheet Samples</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        .sample-list {
            list-style: none;
            padding: 0;
        }
        .sample-list li {
            margin: 15px 0;
        }
        .sample-list a {
            display: block;
            padding: 15px 20px;
            background: #ecf0f1;
            color: #2980b9;
            text-decoration: none;
            border-radius: 5px;
            transition: background-color 0.3s;
        }
        .sample-list a:hover {
            background: #3498db;
            color: white;
        }
        .category {
            margin-top: 25px;
        }
        .category h2 {
            color: #34495e;
            font-size: 1.2em;
            margin-bottom: 10px;
        }
        .version-info {
            color: #7f8c8d;
            font-size: 0.9em;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>PhpSpreadsheet Sample Scripts</h1>
        <p>Welcome to the PhpSpreadsheet sample application. These samples demonstrate various spreadsheet manipulation features.</p>
        
        <div class="category">
            <h2>Format Wizards</h2>
            <ul class="sample-list">
                <li><a href="/samples/Wizards/NumberFormat/Accounting.php">Number Format Wizard - Accounting</a></li>
            </ul>
        </div>
        
        <div class="version-info">
            <p>PhpSpreadsheet Sample Application v2.1.5</p>
            <!-- Developer note: Currency format samples use dropdown for input, but values are not server-validated -->
        </div>
    </div>
</body>
</html>
"""

ACCOUNTING_FORM = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Number Format Wizard - Accounting</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 2px solid #27ae60;
            padding-bottom: 10px;
            font-size: 1.5em;
        }}
        .form-group {{
            margin-bottom: 20px;
        }}
        label {{
            display: block;
            margin-bottom: 5px;
            color: #34495e;
            font-weight: bold;
        }}
        input[type="text"], input[type="number"], select {{
            width: 100%;
            padding: 10px;
            border: 1px solid #bdc3c7;
            border-radius: 4px;
            box-sizing: border-box;
            font-size: 1em;
        }}
        input[type="submit"] {{
            background: #27ae60;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 1em;
        }}
        input[type="submit"]:hover {{
            background: #219a52;
        }}
        .preview-section {{
            margin-top: 20px;
            padding: 15px;
            background: #f9f9f9;
            border-radius: 4px;
            border-left: 4px solid #27ae60;
        }}
        .preview-value {{
            font-size: 1.5em;
            color: #2c3e50;
            font-weight: bold;
        }}
        .result-box {{
            margin-top: 15px;
            padding: 15px;
            border-radius: 4px;
        }}
        .result-box.success {{
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }}
        .result-box.error {{
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }}
        .info-text {{
            color: #0c5460;
        }}
        .flag-text {{
            font-weight: bold;
        }}
        .breadcrumb {{
            margin-bottom: 20px;
            color: #7f8c8d;
        }}
        .breadcrumb a {{
            color: #3498db;
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="breadcrumb">
            <a href="/">Samples</a> &gt; Wizards &gt; NumberFormat &gt; Accounting
        </div>
        
        <h1>Number Format Wizard - Accounting</h1>
        <p>Use this wizard to format numbers in accounting style with currency symbols.</p>
        
        <form method="POST" action="/samples/Wizards/NumberFormat/Accounting.php">
            <div class="form-group">
                <label for="number">Number to format:</label>
                <input type="text" id="number" name="number" value="{number_value}">
            </div>
            
            <div class="form-group">
                <label for="currency">Currency symbol:</label>
                <select id="currency" name="currency">
                    <option value="$">$ (US Dollar)</option>
                    <option value="EUR">EUR (Euro)</option>
                    <option value="GBP">GBP (British Pound)</option>
                    <option value="JPY">JPY (Japanese Yen)</option>
                    <option value="INR">INR (Indian Rupee)</option>
                    <option value="CHF">CHF (Swiss Franc)</option>
                    <option value="AUD">AUD (Australian Dollar)</option>
                    <option value="CAD">CAD (Canadian Dollar)</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="decimals">Decimal places:</label>
                <input type="number" id="decimals" name="decimals" value="{decimals_value}" min="0" max="10">
            </div>
            
            <div class="form-group">
                <label for="position">Currency position:</label>
                <select id="position" name="position">
                    <option value="1">Before number</option>
                    <option value="2">After number</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="spacing">Space between currency and number:</label>
                <select id="spacing" name="spacing">
                    <option value="0">No space</option>
                    <option value="1">With space</option>
                </select>
            </div>
            
            <input type="submit" name="submit" value="Display Mask">
        </form>
        
        <div class="preview-section">
            <label>Preview:</label>
            {formatted_preview}
        </div>
        
        {result_section}
    </div>
</body>
</html>
"""

ACCOUNTING_RESULT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Format Preview</title>
    <style>
        .preview-value {{
            font-size: 2em;
            color: #2c3e50;
            font-weight: bold;
            padding: 20px;
        }}
    </style>
</head>
<body>
    {preview}
</body>
</html>
"""

# Image routes for backward compatibility
IMAGE_ROUTES = {
    "spreadsheet": {
        "start": "static/img/cookies/new_circle.png",
        "process": "static/img/cookies/error_circle.png",
        "error": "static/img/cookies/error_circle.png",
        "success": "static/img/cookies/success_circle.png"
    },
    "xss_easy": {
        "start": "static/img/cookies/new_circle.png",
        "process": "static/img/cookies/error_circle.png",
        "error": "static/img/cookies/error_circle.png",
        "success": "static/img/cookies/success_circle.png"
    }
}
