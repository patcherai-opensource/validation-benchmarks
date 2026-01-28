INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PhpSheet - Spreadsheet Library Demo</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; color: #eee; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        header { text-align: center; padding: 40px 0; border-bottom: 1px solid #333; }
        header h1 { color: #4ecca3; font-size: 2.5em; margin-bottom: 10px; }
        header p { color: #aaa; font-size: 1.1em; }
        nav { background: #232740; padding: 15px 0; margin-bottom: 30px; }
        nav ul { list-style: none; display: flex; justify-content: center; gap: 30px; }
        nav a { color: #4ecca3; text-decoration: none; font-weight: 500; transition: color 0.3s; }
        nav a:hover { color: #fff; }
        .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 40px 0; }
        .feature-card { background: #232740; border-radius: 10px; padding: 25px; transition: transform 0.3s; }
        .feature-card:hover { transform: translateY(-5px); }
        .feature-card h3 { color: #4ecca3; margin-bottom: 15px; }
        .feature-card p { color: #aaa; line-height: 1.6; }
        .samples-section { background: #232740; border-radius: 10px; padding: 30px; margin-top: 30px; }
        .samples-section h2 { color: #4ecca3; margin-bottom: 20px; }
        .sample-list { list-style: none; }
        .sample-list li { padding: 10px 0; border-bottom: 1px solid #333; }
        .sample-list a { color: #fff; text-decoration: none; }
        .sample-list a:hover { color: #4ecca3; }
        footer { text-align: center; padding: 30px; color: #666; margin-top: 50px; border-top: 1px solid #333; }
        .version-badge { background: #4ecca3; color: #1a1a2e; padding: 3px 10px; border-radius: 12px; font-size: 0.8em; }
    </style>
</head>
<body>
    <nav>
        <ul>
            <li><a href="/">Home</a></li>
            <li><a href="/samples">Samples</a></li>
            <li><a href="/docs">Documentation</a></li>
            <li><a href="/api/units">API</a></li>
            <li><a href="/about">About</a></li>
            <li><a href="/contact">Contact</a></li>
        </ul>
    </nav>
    <div class="container">
        <header>
            <h1>PhpSheet <span class="version-badge">v3.6.0</span></h1>
            <p>A powerful library for reading and writing spreadsheet files in PHP</p>
        </header>
        
        <div class="features">
            <div class="feature-card">
                <h3>Excel Support</h3>
                <p>Read and write Excel 2007+ (.xlsx), Excel 5/95/2000 (.xls), and SpreadsheetML (.xml) files.</p>
            </div>
            <div class="feature-card">
                <h3>CSV & ODS</h3>
                <p>Full support for CSV files with custom delimiters and OpenDocument Spreadsheet format.</p>
            </div>
            <div class="feature-card">
                <h3>Engineering Functions</h3>
                <p>Built-in engineering calculation and unit conversion functions for technical applications.</p>
            </div>
        </div>
        
        <div class="samples-section">
            <h2>Sample Applications</h2>
            <ul class="sample-list">
                <li><a href="/samples">View All Samples &rarr;</a></li>
                <li><a href="/samples/Engineering/Convert-Online.php">Engineering: Unit Converter (Online Demo)</a></li>
            </ul>
        </div>
        
        <footer>
            <p>&copy; 2024 PhpSheet Project. Open Source under MIT License.</p>
        </footer>
    </div>
</body>
</html>
"""

ABOUT_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>About - PhpSheet</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; color: #eee; }
        .container { max-width: 800px; margin: 0 auto; padding: 40px 20px; }
        h1 { color: #4ecca3; margin-bottom: 20px; }
        p { line-height: 1.8; color: #aaa; margin-bottom: 15px; }
        a { color: #4ecca3; }
        .back-link { display: inline-block; margin-top: 20px; padding: 10px 20px; background: #4ecca3; color: #1a1a2e; text-decoration: none; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>About PhpSheet</h1>
        <p>PhpSheet is a powerful PHP library designed to read, write, and manipulate spreadsheet files. Originally forked from PHPExcel, it provides robust support for multiple formats including Excel (.xlsx, .xls), OpenDocument (.ods), and CSV.</p>
        <p>The library includes extensive engineering functions for unit conversion, complex calculations, and data transformation.</p>
        <p>Current Version: 3.6.0</p>
        <a href="/" class="back-link">&larr; Back to Home</a>
    </div>
</body>
</html>
"""

DOCS_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Documentation - PhpSheet</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; color: #eee; }
        .container { max-width: 900px; margin: 0 auto; padding: 40px 20px; }
        h1, h2 { color: #4ecca3; margin-bottom: 20px; }
        h2 { margin-top: 30px; font-size: 1.3em; }
        p, li { line-height: 1.8; color: #aaa; }
        ul { margin-left: 20px; margin-bottom: 20px; }
        code { background: #232740; padding: 2px 8px; border-radius: 4px; font-family: monospace; }
        pre { background: #232740; padding: 15px; border-radius: 8px; overflow-x: auto; margin: 15px 0; }
        a { color: #4ecca3; }
        .back-link { display: inline-block; margin-top: 20px; padding: 10px 20px; background: #4ecca3; color: #1a1a2e; text-decoration: none; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Documentation</h1>
        
        <h2>Installation</h2>
        <pre>composer require phpoffice/phpsheet</pre>
        
        <h2>Quick Start</h2>
        <pre>use PhpOffice\\PhpSheet\\Spreadsheet;
use PhpOffice\\PhpSheet\\Writer\\Xlsx;

$spreadsheet = new Spreadsheet();
$sheet = $spreadsheet->getActiveSheet();
$sheet->setCellValue('A1', 'Hello World!');

$writer = new Xlsx($spreadsheet);
$writer->save('hello_world.xlsx');</pre>
        
        <h2>Engineering Functions</h2>
        <p>PhpSheet includes built-in support for engineering calculations:</p>
        <ul>
            <li><code>CONVERT(number, from_unit, to_unit)</code> - Convert between measurement units</li>
            <li><code>DEC2HEX(number)</code> - Convert decimal to hexadecimal</li>
            <li><code>BIN2OCT(number)</code> - Convert binary to octal</li>
        </ul>
        
        <h2>Online Samples</h2>
        <p>Check out our <a href="/samples">sample applications</a> to see PhpSheet in action.</p>
        
        <a href="/" class="back-link">&larr; Back to Home</a>
    </div>
</body>
</html>
"""

CONTACT_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Contact - PhpSheet</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; color: #eee; }
        .container { max-width: 600px; margin: 0 auto; padding: 40px 20px; }
        h1 { color: #4ecca3; margin-bottom: 20px; }
        form { background: #232740; padding: 30px; border-radius: 10px; }
        label { display: block; margin-bottom: 5px; color: #aaa; }
        input, textarea { width: 100%; padding: 12px; margin-bottom: 20px; border: 1px solid #333; border-radius: 5px; background: #1a1a2e; color: #eee; }
        button { background: #4ecca3; color: #1a1a2e; padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }
        a { color: #4ecca3; }
        .back-link { display: inline-block; margin-top: 20px; padding: 10px 20px; background: #4ecca3; color: #1a1a2e; text-decoration: none; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Contact Us</h1>
        <form method="POST">
            <label for="name">Name</label>
            <input type="text" id="name" name="name" required>
            
            <label for="email">Email</label>
            <input type="email" id="email" name="email" required>
            
            <label for="message">Message</label>
            <textarea id="message" name="message" rows="5" required></textarea>
            
            <button type="submit">Send Message</button>
        </form>
        <a href="/" class="back-link">&larr; Back to Home</a>
    </div>
</body>
</html>
"""

CONTACT_SUCCESS = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Message Sent - PhpSheet</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; color: #eee; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; text-align: center; }}
        h1 {{ color: #4ecca3; margin-bottom: 20px; }}
        p {{ color: #aaa; margin-bottom: 15px; }}
        .back-link {{ display: inline-block; margin-top: 20px; padding: 10px 20px; background: #4ecca3; color: #1a1a2e; text-decoration: none; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Message Sent!</h1>
        <p>Thank you for contacting us, {0}.</p>
        <p>We'll respond to {1} as soon as possible.</p>
        <a href="/" class="back-link">&larr; Back to Home</a>
    </div>
</body>
</html>
"""

SAMPLES_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Samples - PhpSheet</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; color: #eee; }
        .container { max-width: 900px; margin: 0 auto; padding: 40px 20px; }
        h1, h2 { color: #4ecca3; margin-bottom: 20px; }
        h2 { margin-top: 30px; font-size: 1.2em; border-bottom: 1px solid #333; padding-bottom: 10px; }
        .sample-grid { display: grid; gap: 15px; margin-top: 20px; }
        .sample-item { background: #232740; padding: 20px; border-radius: 8px; }
        .sample-item a { color: #fff; text-decoration: none; font-weight: 500; }
        .sample-item a:hover { color: #4ecca3; }
        .sample-item p { color: #888; font-size: 0.9em; margin-top: 8px; }
        .back-link { display: inline-block; margin-top: 30px; padding: 10px 20px; background: #4ecca3; color: #1a1a2e; text-decoration: none; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Sample Applications</h1>
        <p style="color: #aaa; margin-bottom: 30px;">Browse our collection of sample applications demonstrating PhpSheet capabilities.</p>
        
        <h2>Basic Examples</h2>
        <div class="sample-grid">
            <div class="sample-item">
                <a href="#">01simple.php</a>
                <p>Basic spreadsheet creation and cell manipulation</p>
            </div>
            <div class="sample-item">
                <a href="#">02types.php</a>
                <p>Working with different cell types (numbers, dates, formulas)</p>
            </div>
        </div>
        
        <h2>Engineering</h2>
        <div class="sample-grid">
            <div class="sample-item">
                <a href="/samples/Engineering/Convert-Online.php">Convert-Online.php</a>
                <p>Interactive unit conversion tool - convert between length, weight, and temperature units</p>
            </div>
            <div class="sample-item">
                <a href="#">Calculate-Complex.php</a>
                <p>Complex number calculations and engineering formulas</p>
            </div>
        </div>
        
        <h2>Charts</h2>
        <div class="sample-grid">
            <div class="sample-item">
                <a href="#">33chartcreate-pie.php</a>
                <p>Create pie charts from spreadsheet data</p>
            </div>
            <div class="sample-item">
                <a href="#">33chartcreate-bar.php</a>
                <p>Generate bar charts with custom styling</p>
            </div>
        </div>
        
        <a href="/" class="back-link">&larr; Back to Home</a>
    </div>
</body>
</html>
"""

CONVERT_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Unit Converter - PhpSheet Engineering Sample</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; color: #eee; }}
        .container {{ max-width: 700px; margin: 0 auto; padding: 40px 20px; }}
        h1 {{ color: #4ecca3; margin-bottom: 10px; }}
        .subtitle {{ color: #888; margin-bottom: 30px; }}
        .converter-box {{ background: #232740; padding: 30px; border-radius: 10px; }}
        .category-tabs {{ display: flex; gap: 10px; margin-bottom: 20px; }}
        .category-tabs a {{ padding: 8px 16px; background: #1a1a2e; color: #aaa; text-decoration: none; border-radius: 5px; }}
        .category-tabs a.active, .category-tabs a:hover {{ background: #4ecca3; color: #1a1a2e; }}
        label {{ display: block; margin-bottom: 5px; color: #aaa; font-size: 0.9em; }}
        input, select {{ width: 100%; padding: 12px; margin-bottom: 20px; border: 1px solid #333; border-radius: 5px; background: #1a1a2e; color: #eee; }}
        .unit-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }}
        button {{ width: 100%; background: #4ecca3; color: #1a1a2e; padding: 14px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; font-size: 1em; }}
        button:hover {{ background: #3db892; }}
        .result-box {{ margin-top: 20px; padding: 15px; background: #1a1a2e; border-radius: 5px; border-left: 4px solid #4ecca3; }}
        .result-box.error {{ border-left-color: #e74c3c; }}
        .result-box.success {{ border-left-color: #2ecc71; background: #1e3a2f; }}
        .result-box.warning {{ border-left-color: #f39c12; }}
        .back-link {{ display: inline-block; margin-top: 20px; padding: 10px 20px; background: #4ecca3; color: #1a1a2e; text-decoration: none; border-radius: 5px; }}
        .path-info {{ color: #666; font-size: 0.8em; margin-bottom: 20px; font-family: monospace; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Unit Converter</h1>
        <p class="subtitle">Engineering Sample - CONVERT() Function Demo</p>
        <p class="path-info">/samples/Engineering/Convert-Online.php</p>
        
        <div class="converter-box">
            <div class="category-tabs">
                <a href="?category=length" class="{length_active}">Length</a>
                <a href="?category=weight" class="{weight_active}">Weight</a>
                <a href="?category=temperature" class="{temp_active}">Temperature</a>
            </div>
            
            <form method="POST">
                <label for="quantity">Quantity</label>
                <input type="text" id="quantity" name="quantity" placeholder="Enter a number..." value="{quantity_value}">
                
                <div class="unit-row">
                    <div>
                        <label for="fromUnit">From Unit</label>
                        <select id="fromUnit" name="fromUnit">
                            {units_options}
                        </select>
                    </div>
                    <div>
                        <label for="toUnit">To Unit</label>
                        <select id="toUnit" name="toUnit">
                            {units_options}
                        </select>
                    </div>
                </div>
                
                <button type="submit">Convert</button>
            </form>
            
            {result}
            {xss_result}
        </div>
        
        <a href="/samples" class="back-link">&larr; Back to Samples</a>
    </div>
</body>
</html>
""".replace("{length_active}", "active").replace("{weight_active}", "").replace("{temp_active}", "")

CONVERT_RESULT_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Conversion Result</title>
</head>
<body>
    <div class="result">
        <p>Quantity: {0}</p>
        <p>From: {1}</p>
        <p>To: {2}</p>
        <div class="output">{3}</div>
    </div>
</body>
</html>
"""

# Image routes for XSS validation feedback
IMAGE_ROUTES = {
    "converter": {
        "start": "static/img/cookies/new_circle.png",
        "process": "static/img/cookies/error_circle.png",
        "error": "static/img/cookies/error_circle.png",
        "success": "static/img/cookies/success_circle.png"
    }
}
