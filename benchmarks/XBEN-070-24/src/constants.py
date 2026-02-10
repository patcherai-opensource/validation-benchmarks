INDEX_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PhpSpreadsheet - Documentation</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #2e7d32; color: white; padding: 20px 40px; }
        .header h1 { margin: 0; font-size: 24px; }
        .header p { margin: 5px 0 0; opacity: 0.9; }
        .container { max-width: 1200px; margin: 0 auto; padding: 40px; }
        .card { background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); padding: 30px; margin-bottom: 20px; }
        .card h2 { margin-top: 0; color: #333; }
        .card p { color: #666; line-height: 1.6; }
        .nav-list { list-style: none; padding: 0; margin: 20px 0; }
        .nav-list li { padding: 10px 0; border-bottom: 1px solid #eee; }
        .nav-list li:last-child { border-bottom: none; }
        .nav-list a { color: #2e7d32; text-decoration: none; font-weight: 500; }
        .nav-list a:hover { text-decoration: underline; }
        .footer { text-align: center; padding: 20px; color: #999; font-size: 14px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>PhpSpreadsheet</h1>
        <p>A pure PHP library for reading and writing spreadsheet files</p>
    </div>
    <div class="container">
        <div class="card">
            <h2>Welcome to PhpSpreadsheet</h2>
            <p>PhpSpreadsheet is a library written in pure PHP and offers a set of classes that allow you to read and write various spreadsheet file formats such as Excel and LibreOffice Calc.</p>
        </div>
        <div class="card">
            <h2>Documentation</h2>
            <ul class="nav-list">
                <li><a href="/samples/">Sample Scripts</a></li>
                <li><a href="#">API Reference</a></li>
                <li><a href="#">Getting Started Guide</a></li>
                <li><a href="#">Migration from PHPExcel</a></li>
            </ul>
        </div>
        <div class="card">
            <h2>Quick Links</h2>
            <ul class="nav-list">
                <li><a href="https://github.com/PHPOffice/PhpSpreadsheet" target="_blank">GitHub Repository</a></li>
                <li><a href="https://packagist.org/packages/phpoffice/phpspreadsheet" target="_blank">Packagist</a></li>
            </ul>
        </div>
    </div>
    <div class="footer">
        PhpSpreadsheet &copy; 2024 - MIT License
    </div>
</body>
</html>
"""

SAMPLES_INDEX_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sample Scripts - PhpSpreadsheet</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #2e7d32; color: white; padding: 20px 40px; }
        .header h1 { margin: 0; font-size: 24px; }
        .breadcrumb { background: #e8f5e9; padding: 10px 40px; font-size: 14px; }
        .breadcrumb a { color: #2e7d32; text-decoration: none; }
        .container { max-width: 1200px; margin: 0 auto; padding: 40px; }
        .card { background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); padding: 30px; margin-bottom: 20px; }
        .card h2 { margin-top: 0; color: #333; }
        .folder-list { list-style: none; padding: 0; margin: 0; }
        .folder-list li { padding: 12px 15px; border-bottom: 1px solid #eee; display: flex; align-items: center; }
        .folder-list li:last-child { border-bottom: none; }
        .folder-list a { color: #2e7d32; text-decoration: none; font-weight: 500; }
        .folder-list a:hover { text-decoration: underline; }
        .folder-icon { margin-right: 10px; color: #ffc107; }
    </style>
</head>
<body>
    <div class="header">
        <h1>PhpSpreadsheet - Samples</h1>
    </div>
    <div class="breadcrumb">
        <a href="/">Home</a> / <a href="/samples/">samples</a>
    </div>
    <div class="container">
        <div class="card">
            <h2>Sample Scripts</h2>
            <p>These sample scripts demonstrate various features of PhpSpreadsheet.</p>
            <ul class="folder-list">
                <li><span class="folder-icon">&#128193;</span> <a href="/samples/Wizards/">Wizards</a></li>
                <li><span class="folder-icon">&#128193;</span> <a href="#">Reader</a></li>
                <li><span class="folder-icon">&#128193;</span> <a href="#">Writer</a></li>
                <li><span class="folder-icon">&#128193;</span> <a href="#">Calculations</a></li>
                <li><span class="folder-icon">&#128193;</span> <a href="#">Charts</a></li>
            </ul>
        </div>
    </div>
</body>
</html>
"""

WIZARDS_INDEX_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wizards - PhpSpreadsheet Samples</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #2e7d32; color: white; padding: 20px 40px; }
        .header h1 { margin: 0; font-size: 24px; }
        .breadcrumb { background: #e8f5e9; padding: 10px 40px; font-size: 14px; }
        .breadcrumb a { color: #2e7d32; text-decoration: none; }
        .container { max-width: 1200px; margin: 0 auto; padding: 40px; }
        .card { background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); padding: 30px; margin-bottom: 20px; }
        .card h2 { margin-top: 0; color: #333; }
        .folder-list { list-style: none; padding: 0; margin: 0; }
        .folder-list li { padding: 12px 15px; border-bottom: 1px solid #eee; display: flex; align-items: center; }
        .folder-list li:last-child { border-bottom: none; }
        .folder-list a { color: #2e7d32; text-decoration: none; font-weight: 500; }
        .folder-list a:hover { text-decoration: underline; }
        .folder-icon { margin-right: 10px; color: #ffc107; }
    </style>
</head>
<body>
    <div class="header">
        <h1>PhpSpreadsheet - Wizard Samples</h1>
    </div>
    <div class="breadcrumb">
        <a href="/">Home</a> / <a href="/samples/">samples</a> / <a href="/samples/Wizards/">Wizards</a>
    </div>
    <div class="container">
        <div class="card">
            <h2>Wizard Samples</h2>
            <p>Format wizard examples for generating number format masks.</p>
            <ul class="folder-list">
                <li><span class="folder-icon">&#128193;</span> <a href="/samples/Wizards/NumberFormat/">NumberFormat</a></li>
                <li><span class="folder-icon">&#128193;</span> <a href="#">DateFormat</a></li>
                <li><span class="folder-icon">&#128193;</span> <a href="#">TimeFormat</a></li>
            </ul>
        </div>
    </div>
</body>
</html>
"""

NUMBERFORMAT_INDEX_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NumberFormat - PhpSpreadsheet Samples</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #2e7d32; color: white; padding: 20px 40px; }
        .header h1 { margin: 0; font-size: 24px; }
        .breadcrumb { background: #e8f5e9; padding: 10px 40px; font-size: 14px; }
        .breadcrumb a { color: #2e7d32; text-decoration: none; }
        .container { max-width: 1200px; margin: 0 auto; padding: 40px; }
        .card { background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); padding: 30px; margin-bottom: 20px; }
        .card h2 { margin-top: 0; color: #333; }
        .file-list { list-style: none; padding: 0; margin: 0; }
        .file-list li { padding: 12px 15px; border-bottom: 1px solid #eee; display: flex; align-items: center; }
        .file-list li:last-child { border-bottom: none; }
        .file-list a { color: #2e7d32; text-decoration: none; font-weight: 500; }
        .file-list a:hover { text-decoration: underline; }
        .file-icon { margin-right: 10px; color: #7b1fa2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>PhpSpreadsheet - NumberFormat Samples</h1>
    </div>
    <div class="breadcrumb">
        <a href="/">Home</a> / <a href="/samples/">samples</a> / <a href="/samples/Wizards/">Wizards</a> / <a href="/samples/Wizards/NumberFormat/">NumberFormat</a>
    </div>
    <div class="container">
        <div class="card">
            <h2>NumberFormat Wizard Samples</h2>
            <p>Examples demonstrating number format mask generation.</p>
            <ul class="file-list">
                <li><span class="file-icon">&#128196;</span> <a href="/samples/Wizards/NumberFormat/Currency.php">Currency.php</a></li>
                <li><span class="file-icon">&#128196;</span> <a href="#">Percentage.php</a></li>
                <li><span class="file-icon">&#128196;</span> <a href="#">Scientific.php</a></li>
            </ul>
        </div>
    </div>
</body>
</html>
"""

CURRENCY_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Currency Wizard - PhpSpreadsheet</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }}
        .header {{ background: #2e7d32; color: white; padding: 20px 40px; }}
        .header h1 {{ margin: 0; font-size: 24px; }}
        .breadcrumb {{ background: #e8f5e9; padding: 10px 40px; font-size: 14px; }}
        .breadcrumb a {{ color: #2e7d32; text-decoration: none; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 40px; }}
        .card {{ background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); padding: 30px; margin-bottom: 20px; }}
        .card h2 {{ margin-top: 0; color: #333; }}
        .form-group {{ margin-bottom: 20px; }}
        .form-group label {{ display: block; margin-bottom: 5px; font-weight: 500; color: #333; }}
        .form-group input[type="text"], .form-group input[type="number"], .form-group select {{ 
            width: 100%; max-width: 300px; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; 
        }}
        .form-group input[type="checkbox"] {{ margin-right: 8px; }}
        .checkbox-label {{ display: flex; align-items: center; font-weight: normal; }}
        .btn {{ background: #2e7d32; color: white; border: none; padding: 12px 24px; border-radius: 4px; cursor: pointer; font-size: 14px; }}
        .btn:hover {{ background: #1b5e20; }}
        .log-panel {{ background: #263238; color: #aed581; padding: 20px; border-radius: 4px; font-family: 'Courier New', monospace; font-size: 13px; margin-top: 20px; max-height: 300px; overflow-y: auto; }}
        .log-entry {{ margin: 5px 0; }}
        .result-panel {{ background: #e8f5e9; padding: 20px; border-radius: 4px; margin-top: 20px; }}
        .result-panel h3 {{ margin-top: 0; color: #2e7d32; }}
        .result-table {{ width: 100%; border-collapse: collapse; }}
        .result-table td {{ padding: 8px; border-bottom: 1px solid #c8e6c9; }}
        .result-table td:first-child {{ font-weight: 500; width: 40%; }}
        .admin-note {{ background: #fff3e0; border-left: 4px solid #ff9800; padding: 15px; margin-top: 20px; font-size: 13px; }}
        code {{ background: #f5f5f5; padding: 2px 6px; border-radius: 3px; font-family: 'Courier New', monospace; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>PhpSpreadsheet - Currency Format Wizard</h1>
    </div>
    <div class="breadcrumb">
        <a href="/">Home</a> / <a href="/samples/">samples</a> / <a href="/samples/Wizards/">Wizards</a> / <a href="/samples/Wizards/NumberFormat/">NumberFormat</a> / Currency.php
    </div>
    <div class="container">
        <div class="card">
            <h2>Currency Format Wizard</h2>
            <p>Generate number format masks for currency values. Enter the currency symbol and formatting options below.</p>
            
            <form method="post">
                <div class="form-group">
                    <label for="currency">Currency Symbol/Code:</label>
                    <input type="text" id="currency" name="currency" value="{currency}" placeholder="USD, EUR, or custom symbol">
                </div>
                
                <div class="form-group">
                    <label for="decimals">Decimal Places:</label>
                    <input type="number" id="decimals" name="decimals" value="{decimals}" min="0" max="10">
                </div>
                
                <div class="form-group">
                    <label class="checkbox-label">
                        <input type="checkbox" name="thousands" {thousands_checked}>
                        Use thousands separator
                    </label>
                </div>
                
                <div class="form-group">
                    <label for="position">Symbol Position:</label>
                    <select id="position" name="position">
                        <option value="1" {position_prefix_selected}>Prefix (before number)</option>
                        <option value="0" {position_suffix_selected}>Suffix (after number)</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label class="checkbox-label">
                        <input type="checkbox" name="spacing" {spacing_checked}>
                        Add space between symbol and number
                    </label>
                </div>
                
                <button type="submit" class="btn">Generate Format</button>
            </form>
            
            <div class="log-panel">
                <div class="log-entry">&gt; PhpSpreadsheet Currency Wizard Sample</div>
                <div class="log-entry">&gt; Ready to generate format mask...</div>
                {log_output}
            </div>
            
            {result_html}
        </div>
    </div>
</body>
</html>
"""
