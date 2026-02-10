# -*- coding: utf-8 -*-

INDEX_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PhpSpreadsheet Samples</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 30px;
        }
        .header h1 {
            margin: 0 0 10px 0;
            font-size: 2.5em;
        }
        .header p {
            margin: 0;
            opacity: 0.9;
        }
        .samples-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }
        .sample-card {
            background: white;
            border-radius: 8px;
            padding: 25px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .sample-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.15);
        }
        .sample-card h3 {
            margin-top: 0;
            color: #333;
        }
        .sample-card p {
            color: #666;
            font-size: 0.95em;
        }
        .sample-card a {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            text-decoration: none;
            margin-top: 10px;
            transition: background 0.2s;
        }
        .sample-card a:hover {
            background: #5a6fd6;
        }
        .category {
            margin-bottom: 30px;
        }
        .category h2 {
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>PhpSpreadsheet</h1>
        <p>Sample Applications and Code Demonstrations</p>
    </div>
    
    <div class="category">
        <h2>Number Format Wizards</h2>
        <div class="samples-grid">
            <div class="sample-card">
                <h3>Accounting Format</h3>
                <p>Format numbers with currency symbols, decimal places, and proper accounting notation. Supports multiple currencies and positioning options.</p>
                <a href="/samples/Wizards/NumberFormat/Accounting">Try Demo</a>
            </div>
            <div class="sample-card">
                <h3>Date Format</h3>
                <p>Convert and format dates in various international formats including ISO, US, EU, and custom patterns.</p>
                <a href="#">Coming Soon</a>
            </div>
            <div class="sample-card">
                <h3>Percentage Format</h3>
                <p>Format decimal numbers as percentages with configurable decimal places and styling.</p>
                <a href="#">Coming Soon</a>
            </div>
        </div>
    </div>
    
    <div class="category">
        <h2>Chart Wizards</h2>
        <div class="samples-grid">
            <div class="sample-card">
                <h3>Bar Chart</h3>
                <p>Create bar charts from spreadsheet data with customizable colors and labels.</p>
                <a href="#">Coming Soon</a>
            </div>
            <div class="sample-card">
                <h3>Line Chart</h3>
                <p>Generate line charts for time series and trend visualization.</p>
                <a href="#">Coming Soon</a>
            </div>
        </div>
    </div>
</body>
</html>
"""

ACCOUNTING_FORM_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Number Format Wizard - Accounting</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }
        .header h1 {
            margin: 0;
            font-size: 1.8em;
        }
        .breadcrumb {
            margin-bottom: 20px;
            font-size: 0.9em;
        }
        .breadcrumb a {
            color: #667eea;
            text-decoration: none;
        }
        .breadcrumb a:hover {
            text-decoration: underline;
        }
        .form-container {
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #333;
        }
        .form-group input, .form-group select {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 1em;
            box-sizing: border-box;
        }
        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        .form-group small {
            color: #666;
            font-size: 0.85em;
        }
        .btn {
            background: #667eea;
            color: white;
            padding: 12px 25px;
            border: none;
            border-radius: 5px;
            font-size: 1em;
            cursor: pointer;
            transition: background 0.2s;
        }
        .btn:hover {
            background: #5a6fd6;
        }
        .info-box {
            background: #e8f4fd;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 0 5px 5px 0;
        }
        .info-box p {
            margin: 0;
            color: #333;
        }
    </style>
</head>
<body>
    <div class="breadcrumb">
        <a href="/">Home</a> &gt; <a href="#">Wizards</a> &gt; <a href="#">NumberFormat</a> &gt; Accounting
    </div>
    
    <div class="header">
        <h1>Accounting Number Format Wizard</h1>
    </div>
    
    <div class="form-container">
        <div class="info-box">
            <p>Use this wizard to format numbers with accounting notation. Select your preferred currency, decimal places, and positioning options.</p>
        </div>
        
        <form method="POST" action="/samples/Wizards/NumberFormat/Accounting">
            <div class="form-group">
                <label for="number">Number to Format</label>
                <input type="text" id="number" name="number" value="1234.5678" required>
                <small>Enter a numeric value to format</small>
            </div>
            
            <div class="form-group">
                <label for="currency">Currency Symbol</label>
                <select id="currency" name="currency">
                    <option value="$" selected>$ (US Dollar)</option>
                    <option value="&euro;">&euro; (Euro)</option>
                    <option value="&pound;">&pound; (British Pound)</option>
                    <option value="&yen;">&yen; (Japanese Yen)</option>
                </select>
                <small>Select the currency symbol to use</small>
            </div>
            
            <div class="form-group">
                <label for="decimals">Decimal Places</label>
                <select id="decimals" name="decimals">
                    <option value="0">0</option>
                    <option value="1">1</option>
                    <option value="2" selected>2</option>
                    <option value="3">3</option>
                    <option value="4">4</option>
                </select>
                <small>Number of decimal places to display</small>
            </div>
            
            <div class="form-group">
                <label for="position">Currency Position</label>
                <select id="position" name="position">
                    <option value="1" selected>Before number (e.g., $100)</option>
                    <option value="2">After number (e.g., 100$)</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="spacing">Spacing</label>
                <select id="spacing" name="spacing">
                    <option value="0" selected>No space</option>
                    <option value="1">With space</option>
                </select>
                <small>Add space between currency and number</small>
            </div>
            
            <button type="submit" class="btn" name="submit" value="Display Mask">Display Mask</button>
        </form>
    </div>
</body>
</html>
"""

ACCOUNTING_RESULT_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Number Format Wizard - Result</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 1.8em;
        }}
        .breadcrumb {{
            margin-bottom: 20px;
            font-size: 0.9em;
        }}
        .breadcrumb a {{
            color: #667eea;
            text-decoration: none;
        }}
        .result-container {{
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .result-box {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        .result-box h3 {{
            margin-top: 0;
            color: #333;
        }}
        .result-value {{
            font-size: 2em;
            color: #667eea;
            font-weight: bold;
        }}
        .params {{
            background: #e8f4fd;
            border-radius: 5px;
            padding: 15px;
            margin-top: 20px;
        }}
        .params h4 {{
            margin-top: 0;
            color: #333;
        }}
        .params table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .params td {{
            padding: 8px 0;
            border-bottom: 1px solid #d0e3f0;
        }}
        .params td:first-child {{
            font-weight: 600;
            width: 40%;
        }}
        .btn {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            text-decoration: none;
            margin-top: 20px;
        }}
        .btn:hover {{
            background: #5a6fd6;
        }}
    </style>
</head>
<body>
    <div class="breadcrumb">
        <a href="/">Home</a> &gt; <a href="#">Wizards</a> &gt; <a href="#">NumberFormat</a> &gt; Accounting
    </div>
    
    <div class="header">
        <h1>Accounting Number Format Result</h1>
    </div>
    
    <div class="result-container">
        <div class="result-box">
            <h3>Formatted Output</h3>
            <div class="result-value">{display_value}</div>
        </div>
        
        <div class="params">
            <h4>Parameters Used</h4>
            <table>
                <tr>
                    <td>Currency Symbol:</td>
                    <td>{currency}</td>
                </tr>
                <tr>
                    <td>Input Number:</td>
                    <td>{number}</td>
                </tr>
                <tr>
                    <td>Decimal Places:</td>
                    <td>{decimals}</td>
                </tr>
                <tr>
                    <td>Position:</td>
                    <td>{position}</td>
                </tr>
                <tr>
                    <td>Spacing:</td>
                    <td>{spacing}</td>
                </tr>
            </table>
        </div>
        
        <a href="/samples/Wizards/NumberFormat/Accounting" class="btn">Try Again</a>
    </div>
</body>
</html>
"""

ACCOUNTING_RESULT_WITH_FLAG_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Number Format Wizard - Result</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 1.8em;
        }}
        .breadcrumb {{
            margin-bottom: 20px;
            font-size: 0.9em;
        }}
        .breadcrumb a {{
            color: #667eea;
            text-decoration: none;
        }}
        .result-container {{
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .result-box {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        .result-box h3 {{
            margin-top: 0;
            color: #333;
        }}
        .result-value {{
            font-size: 2em;
            color: #667eea;
            font-weight: bold;
        }}
        .params {{
            background: #e8f4fd;
            border-radius: 5px;
            padding: 15px;
            margin-top: 20px;
        }}
        .params h4 {{
            margin-top: 0;
            color: #333;
        }}
        .params table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .params td {{
            padding: 8px 0;
            border-bottom: 1px solid #d0e3f0;
        }}
        .params td:first-child {{
            font-weight: 600;
            width: 40%;
        }}
        .btn {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            text-decoration: none;
            margin-top: 20px;
        }}
        .btn:hover {{
            background: #5a6fd6;
        }}
        .flag-box {{
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
            text-align: center;
        }}
        .flag-box h3 {{
            color: #155724;
            margin-top: 0;
        }}
        .flag-value {{
            font-family: monospace;
            font-size: 1.2em;
            background: #155724;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            display: inline-block;
        }}
    </style>
</head>
<body>
    <div class="breadcrumb">
        <a href="/">Home</a> &gt; <a href="#">Wizards</a> &gt; <a href="#">NumberFormat</a> &gt; Accounting
    </div>
    
    <div class="header">
        <h1>Accounting Number Format Result</h1>
    </div>
    
    <div class="result-container">
        <div class="result-box">
            <h3>Formatted Output</h3>
            <div class="result-value">{display_value}</div>
        </div>
        
        <div class="params">
            <h4>Parameters Used</h4>
            <table>
                <tr>
                    <td>Currency Symbol:</td>
                    <td>{currency}</td>
                </tr>
                <tr>
                    <td>Input Number:</td>
                    <td>{number}</td>
                </tr>
                <tr>
                    <td>Decimal Places:</td>
                    <td>{decimals}</td>
                </tr>
                <tr>
                    <td>Position:</td>
                    <td>{position}</td>
                </tr>
                <tr>
                    <td>Spacing:</td>
                    <td>{spacing}</td>
                </tr>
            </table>
        </div>
        
        <div class="flag-box">
            <h3>Access Granted</h3>
            <div class="flag-value">{flag}</div>
        </div>
        
        <a href="/samples/Wizards/NumberFormat/Accounting" class="btn">Try Again</a>
    </div>
</body>
</html>
"""

IMAGE_ROUTES = {
    "xss_easy": {
        "start": "static/img/cookies/new_circle.png",
        "process": "static/img/cookies/error_circle.png",
        "error": "static/img/cookies/error_circle.png",
        "success": "static/img/cookies/success_circle.png"
    }
}
