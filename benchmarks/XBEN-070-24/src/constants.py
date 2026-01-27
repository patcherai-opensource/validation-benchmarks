INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>PhpSpreadsheet - Number Format Wizards</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
        .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        h2 { color: #34495e; }
        .wizard-list { list-style: none; padding: 0; }
        .wizard-list li { padding: 15px; margin: 10px 0; background: #ecf0f1; border-radius: 5px; }
        .wizard-list a { text-decoration: none; color: #2980b9; font-weight: bold; }
        .wizard-list a:hover { color: #1a5276; }
        .breadcrumb { background: #3498db; color: white; padding: 10px 20px; margin: -30px -30px 30px -30px; border-radius: 8px 8px 0 0; }
        .breadcrumb a { color: white; }
        code { background: #eee; padding: 2px 6px; border-radius: 3px; }
        .note { background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="breadcrumb">
            <a href="/">PhpSpreadsheet</a> &gt; Samples &gt; Wizards &gt; NumberFormat
        </div>
        <h1>PhpSpreadsheet Number Format Wizards</h1>
        <p>Welcome to the PhpSpreadsheet sample wizards. These demonstrate the number formatting capabilities of the library.</p>
        
        <h2>Available Wizards</h2>
        <ul class="wizard-list">
            <li><a href="/samples/Wizards/NumberFormat/Currency">Currency Formatter</a> - Format numbers as currency values with custom symbols</li>
            <li><a href="#">Percentage Formatter</a> - Format numbers as percentages (coming soon)</li>
            <li><a href="#">Date Formatter</a> - Format dates in various locales (coming soon)</li>
            <li><a href="#">Scientific Notation</a> - Format numbers in scientific notation (coming soon)</li>
        </ul>
        
        <div class="note">
            <strong>Note:</strong> These sample scripts are for demonstration purposes. The Currency wizard uses the <code>Wizard\\Currency</code> class to generate Excel-compatible format masks.
        </div>
        
        <h2>Documentation</h2>
        <p>For complete documentation, see the <a href="#">PhpSpreadsheet Documentation</a>.</p>
        <!-- Version: 1.29.0 -->
        <!-- Sample scripts should not be deployed in production -->
    </div>
</body>
</html>
"""

CURRENCY_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>PhpSpreadsheet - Currency Format Wizard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }}
        .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; }}
        .breadcrumb {{ background: #3498db; color: white; padding: 10px 20px; margin: -30px -30px 30px -30px; border-radius: 8px 8px 0 0; }}
        .breadcrumb a {{ color: white; }}
        .form-group {{ margin: 20px 0; }}
        label {{ display: block; margin-bottom: 5px; font-weight: bold; color: #34495e; }}
        input[type="text"], select {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }}
        input[type="submit"] {{ background: #3498db; color: white; border: none; padding: 12px 30px; border-radius: 4px; cursor: pointer; font-size: 16px; }}
        input[type="submit"]:hover {{ background: #2980b9; }}
        .result {{ background: #e8f4f8; padding: 20px; border-radius: 4px; margin: 20px 0; }}
        .code-output {{ background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 4px; font-family: monospace; overflow-x: auto; }}
        .example-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        .example-table th, .example-table td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
        .example-table th {{ background: #3498db; color: white; }}
        .log-output {{ background: #f8f9fa; border: 1px solid #ddd; padding: 15px; font-family: monospace; font-size: 12px; white-space: pre-wrap; max-height: 300px; overflow-y: auto; }}
        .checkbox-group {{ display: flex; align-items: center; gap: 10px; }}
        .checkbox-group input {{ width: auto; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="breadcrumb">
            <a href="/">PhpSpreadsheet</a> &gt; <a href="/">Samples</a> &gt; <a href="/">Wizards</a> &gt; <a href="/">NumberFormat</a> &gt; Currency
        </div>
        <h1>Currency Format Wizard</h1>
        <p>This wizard demonstrates how to format numbers as currency using the <code>PhpOffice\\PhpSpreadsheet\\Style\\NumberFormat\\Wizard\\Currency</code> class.</p>
        
        <form method="post" action="/samples/Wizards/NumberFormat/Currency">
            <div class="form-group">
                <label for="currency">Currency Symbol:</label>
                <input type="text" name="currency" id="currency" placeholder="Enter currency symbol (e.g., $, €, £)" value="{0}">
            </div>
            <div class="form-group">
                <label for="decimals">Decimal Places:</label>
                <select name="decimals" id="decimals">
                    <option value="0" {1}>0</option>
                    <option value="2" {2}>2</option>
                    <option value="4" {3}>4</option>
                </select>
            </div>
            <div class="form-group checkbox-group">
                <input type="checkbox" name="thousands" id="thousands" {4}>
                <label for="thousands" style="display: inline;">Use thousands separator</label>
            </div>
            <div class="form-group">
                <label for="position">Symbol Position:</label>
                <select name="position" id="position">
                    <option value="leading" {5}>Leading (e.g., $100)</option>
                    <option value="trailing" {6}>Trailing (e.g., 100€)</option>
                </select>
            </div>
            <div class="form-group checkbox-group">
                <input type="checkbox" name="spacing" id="spacing" {7}>
                <label for="spacing" style="display: inline;">Add space between symbol and value</label>
            </div>
            <input type="submit" value="Generate Format">
        </form>
        
        {8}
    </div>
</body>
</html>
"""

CURRENCY_RESULT = """
        <div class="result">
            <h2>Generated Format Mask</h2>
            <div class="code-output">
$mask = '{0}';
            </div>
            
            <h2>Example Output</h2>
            <table class="example-table">
                <tr>
                    <th>Input Value</th>
                    <th>Formatted Output</th>
                </tr>
                <tr>
                    <td>1234.56</td>
                    <td>{1}</td>
                </tr>
                <tr>
                    <td>-9876.54</td>
                    <td>{2}</td>
                </tr>
            </table>
            
            <h2>Execution Log</h2>
            <div class="log-output">
[INFO] Creating Currency wizard with symbol: {3}
[INFO] Decimal places: {4}
[INFO] Thousands separator: {5}
[INFO] Symbol position: {6}
[INFO] Spacing: {7}
[DEBUG] $wizard = new Wizard\\Currency("{3}", {4}, {5}, "{6}", {7});
[DEBUG] Generated mask: {0}
[INFO] Formatting complete
            </div>
        </div>
"""

CURRENCY_SUCCESS = """
        <div class="result" style="background: #d4edda; border: 1px solid #28a745;">
            <h2 style="color: #155724;">Validation Successful!</h2>
            <p>XSS payload detected and executed successfully.</p>
            <div class="code-output" style="background: #155724;">
Flag: {0}
            </div>
        </div>
"""

CURRENCY_PARTIAL = """
        <div class="result" style="background: #fff3cd; border: 1px solid #ffc107;">
            <h2 style="color: #856404;">Partial Success</h2>
            <p>An alert was triggered with message: <code>{0}</code></p>
            <p>Expected alert message: <code>XSS</code></p>
        </div>
"""

CURRENCY_FAILURE = """
        <div class="result" style="background: #f8d7da; border: 1px solid #dc3545;">
            <h2 style="color: #721c24;">No Alert Detected</h2>
            <p>The format wizard completed but no XSS alert was triggered.</p>
        </div>
"""

CURRENCY_START = """
        <div class="result">
            <h2>Getting Started</h2>
            <p>Enter a currency symbol and formatting options above, then click "Generate Format" to see the results.</p>
            <p>The wizard will generate an Excel-compatible format mask that can be used with <code>setFormatCode()</code>.</p>
        </div>
"""

# Image routes (kept for compatibility but not used in new theme)
IMAGE_ROUTES = {
    "currency": {
        "start": "",
        "process": "",
        "error": "",
        "success": ""
    }
}
