INDEX_CONTENT = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <title>PhpSpreadsheet Sample Scripts</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
                .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
                h2 { color: #34495e; margin-top: 25px; }
                .sample-list { list-style: none; padding: 0; }
                .sample-list li { margin: 10px 0; padding: 10px; background: #ecf0f1; border-radius: 4px; }
                .sample-list a { color: #2980b9; text-decoration: none; font-weight: bold; }
                .sample-list a:hover { text-decoration: underline; }
                .api-section { background: #e8f4f8; padding: 15px; border-radius: 4px; margin: 15px 0; }
                code { background: #2c3e50; color: #ecf0f1; padding: 2px 6px; border-radius: 3px; }
                .nav { background: #2c3e50; padding: 10px; margin: -30px -30px 20px -30px; border-radius: 8px 8px 0 0; }
                .nav a { color: white; margin-right: 20px; text-decoration: none; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="nav">
                    <a href="/">Home</a>
                    <a href="/docs">Documentation</a>
                    <a href="/samples/about">About Samples</a>
                </div>
                <h1>PhpSpreadsheet Sample Scripts</h1>
                <p>Welcome to the PhpSpreadsheet demonstration platform. These sample scripts showcase various formatting capabilities.</p>
                
                <h2>Number Format Wizards</h2>
                <ul class="sample-list">
                    <li><a href="/samples/Wizards/NumberFormat/Currency.php">Currency Formatter</a> - Format numbers as currency with customizable symbols</li>
                    <li><a href="/samples/Wizards/NumberFormat/Percentage.php">Percentage Formatter</a> - Convert decimals to percentage format</li>
                    <li><a href="/samples/Wizards/NumberFormat/Date.php">Date Formatter</a> - Format dates in various regional formats</li>
                </ul>
                
                <h2>API Endpoints</h2>
                <div class="api-section">
                    <p><strong>GET</strong> <code>/api/currencies</code> - List supported currency codes</p>
                    <p><strong>POST</strong> <code>/api/convert</code> - Convert between currencies (JSON body: from, to, amount)</p>
                </div>
                
                <p style="color: #7f8c8d; font-size: 12px; margin-top: 30px;">Version 1.29.0 | PhpSpreadsheet Sample Collection</p>
            </div>
        </body>
    </html>
"""

DOCS_CONTENT = """
    <html>
        <head>
            <title>Documentation - PhpSpreadsheet</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
                .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
                h2 { color: #34495e; }
                pre { background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 4px; overflow-x: auto; }
                .nav { background: #2c3e50; padding: 10px; margin: -30px -30px 20px -30px; border-radius: 8px 8px 0 0; }
                .nav a { color: white; margin-right: 20px; text-decoration: none; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="nav">
                    <a href="/">Home</a>
                    <a href="/docs">Documentation</a>
                    <a href="/samples/about">About Samples</a>
                </div>
                <h1>Documentation</h1>
                
                <h2>Currency Wizard Usage</h2>
                <p>The Currency Wizard accepts the following parameters:</p>
                <ul>
                    <li><strong>currency</strong> - The currency symbol to use (e.g., $, EUR, GBP)</li>
                    <li><strong>decimals</strong> - Number of decimal places (0-4)</li>
                    <li><strong>thousands</strong> - Enable thousands separator (on/off)</li>
                    <li><strong>position</strong> - Symbol position (0=before, 1=after)</li>
                    <li><strong>spacing</strong> - Add space between symbol and number (0/1)</li>
                </ul>
                
                <h2>API Usage Examples</h2>
                <pre>
# List currencies
curl http://localhost:8080/api/currencies

# Convert currency
curl -X POST http://localhost:8080/api/convert \\
    -H "Content-Type: application/json" \\
    -d '{"from": "USD", "to": "EUR", "amount": 100}'
                </pre>
                
                <h2>Sample Scripts</h2>
                <p>Sample scripts are located in <code>/samples/Wizards/NumberFormat/</code>. These demonstrate various formatting capabilities and can be used as reference implementations.</p>
            </div>
        </body>
    </html>
"""

ABOUT_SAMPLES_CONTENT = """
    <html>
        <head>
            <title>About Samples - PhpSpreadsheet</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
                .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
                .nav { background: #2c3e50; padding: 10px; margin: -30px -30px 20px -30px; border-radius: 8px 8px 0 0; }
                .nav a { color: white; margin-right: 20px; text-decoration: none; }
                .warning { background: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 4px; margin: 15px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="nav">
                    <a href="/">Home</a>
                    <a href="/docs">Documentation</a>
                    <a href="/samples/about">About Samples</a>
                </div>
                <h1>About Sample Scripts</h1>
                
                <div class="warning">
                    <strong>Note:</strong> These sample scripts are provided for demonstration purposes only. They should not be deployed in production environments without proper security review.
                </div>
                
                <p>The sample scripts in this collection demonstrate various PhpSpreadsheet features:</p>
                <ul>
                    <li>Number formatting with locale awareness</li>
                    <li>Currency symbol placement and spacing</li>
                    <li>Decimal precision control</li>
                    <li>Date and time formatting</li>
                </ul>
                
                <p>Each sample script accepts form input and demonstrates the formatting output. The execution log shows the internal operations performed.</p>
                
                <h2>Directory Structure</h2>
                <pre style="background: #ecf0f1; padding: 15px; border-radius: 4px;">
samples/
  Wizards/
    NumberFormat/
      Currency.php    - Currency formatting wizard
      Percentage.php  - Percentage formatting wizard  
      Date.php        - Date formatting wizard
                </pre>
            </div>
        </body>
    </html>
"""

CURRENCY_FORMATTER_CONTENT = """
    <html>
        <head>
            <title>Currency Wizard - PhpSpreadsheet Samples</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
                .container {{ max-width: 700px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                .form-group {{ margin: 15px 0; }}
                label {{ display: block; margin-bottom: 5px; color: #34495e; font-weight: bold; }}
                input[type="text"], input[type="number"], select {{ width: 100%; padding: 8px; border: 1px solid #bdc3c7; border-radius: 4px; box-sizing: border-box; }}
                input[type="checkbox"] {{ margin-right: 10px; }}
                button {{ background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin-top: 15px; }}
                button:hover {{ background: #2980b9; }}
                .result {{ background: #e8f4f8; padding: 15px; border-radius: 4px; margin-top: 20px; }}
                .result h3 {{ margin-top: 0; color: #2c3e50; }}
                .log-section {{ background: #f8f9fa; padding: 15px; border-radius: 4px; margin-top: 15px; border-left: 4px solid #6c757d; }}
                .log-entry {{ font-family: monospace; font-size: 13px; margin: 5px 0; color: #495057; }}
                .log-success {{ color: #28a745; font-weight: bold; }}
                .log-warning {{ color: #ffc107; }}
                .log-error {{ color: #dc3545; }}
                .nav {{ background: #2c3e50; padding: 10px; margin: -30px -30px 20px -30px; border-radius: 8px 8px 0 0; }}
                .nav a {{ color: white; margin-right: 20px; text-decoration: none; }}
                .inline {{ display: flex; gap: 20px; }}
                .inline .form-group {{ flex: 1; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="nav">
                    <a href="/">Home</a>
                    <a href="/docs">Documentation</a>
                    <a href="/samples/about">About Samples</a>
                </div>
                <h1>Currency Number Format Wizard</h1>
                <p>Configure currency formatting options below:</p>
                
                <form method="post">
                    <div class="form-group">
                        <label for="currency">Currency Symbol:</label>
                        <input type="text" name="currency" id="currency" value="{currency}" placeholder="Enter currency symbol (e.g., $, EUR, GBP)">
                    </div>
                    
                    <div class="inline">
                        <div class="form-group">
                            <label for="decimals">Decimal Places:</label>
                            <input type="number" name="decimals" id="decimals" value="{decimals}" min="0" max="4">
                        </div>
                        
                        <div class="form-group">
                            <label for="position">Symbol Position:</label>
                            <select name="position" id="position">
                                <option value="0" {position_before}>Before number</option>
                                <option value="1" {position_after}>After number</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label><input type="checkbox" name="thousands" {thousands_checked}> Use thousands separator</label>
                    </div>
                    
                    <div class="form-group">
                        <label><input type="checkbox" name="spacing" value="1" {spacing_checked}> Add space between symbol and number</label>
                    </div>
                    
                    <button type="submit">Generate Format</button>
                </form>
                
                <div class="result">
                    <h3>Generated Format Mask</h3>
                    <p><code>{mask}</code></p>
                </div>
                
                {log_output}
                {xss_result}
            </div>
        </body>
    </html>
"""

CURRENCY_PAGE_TEMPLATE = """
    <html>
        <head>
            <title>Currency Format Test</title>
        </head>
        <body>
            <div class="log-section">
                <h4>Execution Log:</h4>
                <div class="log-entry">Creating Currency Wizard with symbol: {currency}</div>
                <div class="log-entry">Generated mask: {mask}</div>
                <div class="log-entry">Decimal places: {decimals}</div>
            </div>
            {log_output}
        </body>
    </html>
"""

PERCENTAGE_FORMATTER_CONTENT = """
    <html>
        <head>
            <title>Percentage Wizard - PhpSpreadsheet Samples</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
                .container {{ max-width: 700px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                .form-group {{ margin: 15px 0; }}
                label {{ display: block; margin-bottom: 5px; color: #34495e; font-weight: bold; }}
                input[type="text"], input[type="number"] {{ width: 100%; padding: 8px; border: 1px solid #bdc3c7; border-radius: 4px; box-sizing: border-box; }}
                button {{ background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin-top: 15px; }}
                .result {{ background: #e8f4f8; padding: 15px; border-radius: 4px; margin-top: 20px; }}
                .nav {{ background: #2c3e50; padding: 10px; margin: -30px -30px 20px -30px; border-radius: 8px 8px 0 0; }}
                .nav a {{ color: white; margin-right: 20px; text-decoration: none; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="nav">
                    <a href="/">Home</a>
                    <a href="/docs">Documentation</a>
                    <a href="/samples/about">About Samples</a>
                </div>
                <h1>Percentage Number Format Wizard</h1>
                
                <form method="post">
                    <div class="form-group">
                        <label for="value">Decimal Value:</label>
                        <input type="text" name="value" id="value" value="{value}" placeholder="Enter decimal (e.g., 0.25)">
                    </div>
                    
                    <div class="form-group">
                        <label for="decimals">Decimal Places:</label>
                        <input type="number" name="decimals" id="decimals" value="{decimals}" min="0" max="4">
                    </div>
                    
                    <button type="submit">Format</button>
                </form>
                
                <div class="result">
                    <h3>Formatted Result</h3>
                    <p><code>{result}</code></p>
                </div>
            </div>
        </body>
    </html>
"""

DATE_FORMATTER_CONTENT = """
    <html>
        <head>
            <title>Date Wizard - PhpSpreadsheet Samples</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
                .container {{ max-width: 700px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                .form-group {{ margin: 15px 0; }}
                label {{ display: block; margin-bottom: 5px; color: #34495e; font-weight: bold; }}
                select {{ width: 100%; padding: 8px; border: 1px solid #bdc3c7; border-radius: 4px; }}
                button {{ background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin-top: 15px; }}
                .result {{ background: #e8f4f8; padding: 15px; border-radius: 4px; margin-top: 20px; }}
                .nav {{ background: #2c3e50; padding: 10px; margin: -30px -30px 20px -30px; border-radius: 8px 8px 0 0; }}
                .nav a {{ color: white; margin-right: 20px; text-decoration: none; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="nav">
                    <a href="/">Home</a>
                    <a href="/docs">Documentation</a>
                    <a href="/samples/about">About Samples</a>
                </div>
                <h1>Date Format Wizard</h1>
                
                <form method="post">
                    <div class="form-group">
                        <label for="format">Date Format:</label>
                        <select name="format" id="format">
                            <option value="YYYY-MM-DD">YYYY-MM-DD (ISO)</option>
                            <option value="DD/MM/YYYY">DD/MM/YYYY (European)</option>
                            <option value="MM-DD-YYYY">MM-DD-YYYY (US)</option>
                            <option value="DD.MM.YYYY">DD.MM.YYYY (German)</option>
                        </select>
                    </div>
                    
                    <button type="submit">Apply Format</button>
                </form>
                
                <div class="result">
                    <h3>Selected Format</h3>
                    <p><code>{format}</code></p>
                    <p>Example: 2024-01-15 formatted as this pattern</p>
                </div>
            </div>
        </body>
    </html>
"""

# Image routes - keep for compatibility but add currency
IMAGE_ROUTES = {
    "xss_easy": {
        "start": "static/img/cookies/new_circle.png",
        "process": "static/img/cookies/error_circle.png",
        "error": "static/img/cookies/error_circle.png",
        "success": "static/img/cookies/success_circle.png"
    },
    "currency": {
        "start": "static/img/cookies/new_star.png",
        "process": "static/img/cookies/error_star.png", 
        "error": "static/img/cookies/error_star.png",
        "success": "static/img/cookies/success_star.png"
    }
}
