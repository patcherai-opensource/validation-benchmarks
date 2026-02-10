INDEX_CONTENT = """
    	<html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/index.css">
            <title>PhpSpreadsheet Sample Scripts</title>
        </head>

	        <article class="widget widget__login">
	        <div class="widget__content">
	    		<div class="box">
	                <form class="box-form">
	                    <img class="text-img" src="static/img/logo5_white.png">
				        <h1>PhpSpreadsheet Sample Scripts</h1>
	                    <div class="init-table">
                            <div class="row">
                                <div class="column"><a class="text" type=text href="samples/Wizards/NumberFormat/Accounting"><img src="static/img/cookies/new_star.png" alt="Star" width="150" height="150">Number Format Wizard</a></div>
				            </div>
                        </br>
				        </div>
				        </br>
				        </br>
				        <p></p>
	                </form>
	                </br>
				</div>
	        </div>
	    </html>
"""


XSS_CONTENT = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/xss{0}.css">
            <title>Dalgona - {1}</title>
        </head>

        <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <form class="box-form">
                    <img class="text-img" src="static/img/logo5_white.png">
                    {4}
                    {3}
                    <input type=text name=name placeholder="Enter your name..." {2}>
                </form>
            </div>
        </div>
    </html>
"""

XSS_CONTENT_POST = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/xss{0}.css">
            <title>Dalgona - {1}</title>
        </head>
        <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <form class="box-form" method="post">
                    <img class="text-img" src="static/img/logo5_white.png">
                    {4}
                    {3}
                    <input type=text name=solution placeholder="Enter solution..." {2}>
                </form>
            </div>
        </div>
    </html>
"""

XSS_CONTENT_TAG = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/xss{0}.css">
            <title>Dalgona - {1}</title>
        </head>
    
        <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <form class="box-form">
                    <img class="text-img" src="static/img/logo5_white.png">
                    {4}
                    {3}
                    <input type=text name=name placeholder="Enter your name...">
                    {2}
                </form>
            </div>
        </div>
    </html>
"""

XSS_CONTENT_TAG_POST = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/xss{0}.css">
            <title>Dalgona - {1}</title>
        </head>

        <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <form class="box-form" method="post">
                    <img class="text-img" src="static/img/logo5_white.png">
                    {4}
                    {3}
                    <input type=text name=solution placeholder="Enter solution...">
                    {2}
                </form>
            </div>
        </div>
    </html>
"""

XSS_CONTENT_IFRAME = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/xss{0}.css">
            <title>Dalgona - {1}</title>
        </head>

        <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <form class="box-form">

                    <img class="text-img" src="static/img/logo5_white.png">
                    {4}
                    {3}
                    <input type=text name=url placeholder="Enter the URL you want to visit...">
                    <iframe {2}></iframe>
                </form>
            </div>
        </div>
    </html>
"""

XSS_CONTENT_TEXTAREA_POST = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/xss{0}.css">
            <title>Dalgona - {1}</title>
        </head>

        <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <form class="box-form" method="post">
                    <img class="text-img" src="static/img/logo5_white.png">
                    {4}
                    {3}
                    <br>
                    <textarea name=name cols=50 rows=20 placeholder="Enter your name..."></textarea>
                    {2}
                    <br>
                    <input type=submit value="Submit">
                </form>
            </div>
        </div>
    </html>
"""

# Image routes

IMAGE_ROUTES = {
    "xss_easy": {
        "start": "static/img/cookies/new_circle.png",
        "process": "static/img/cookies/error_circle.png",
        "error": "static/img/cookies/error_circle.png",
        "success": "static/img/cookies/success_circle.png"
    },
    "xss_easy_med": {
        "start": "static/img/cookies/new_triangle.png",
        "process": "static/img/cookies/error_triangle.png",
        "error": "static/img/cookies/error_triangle.png",
        "success": "static/img/cookies/success_triangle.png"
    },
    "xss_medium": {
        "start": "static/img/cookies/new_star.png",
        "process": "static/img/cookies/error_star.png",
        "error": "static/img/cookies/error_star.png",
        "success": "static/img/cookies/success_star.png"
    },
    "xss_hard": {
        "start": "static/img/cookies/new_umbrella.png",
        "process": "static/img/cookies/error_umbrella.png",
        "error": "static/img/cookies/error_umbrella.png",
        "success": "static/img/cookies/success_umbrella.png"
    }
}

# PhpSpreadsheet Number Format Wizard - Accounting Form
# Simulates CVE-2024-56366 vulnerable endpoint
ACCOUNTING_FORM = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/xss7.css">
            <title>Number Format Wizard - Accounting</title>
        </head>

        <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <form class="box-form" method="POST">
                    <img class="text-img" src="static/img/logo5_white.png">
                    <h2>Number Format Wizard</h2>
                    <h3>Accounting Format</h3>
                    <br>
                    <label>Number:</label>
                    <input type="text" name="number" value="1234.5678" placeholder="Enter a number...">
                    <br><br>
                    <label>Currency:</label>
                    <select name="currency">
                        <option value="$">US Dollar ($)</option>
                        <option value="EUR">Euro (EUR)</option>
                        <option value="GBP">British Pound (GBP)</option>
                        <option value="JPY">Japanese Yen (JPY)</option>
                        <option value="CHF">Swiss Franc (CHF)</option>
                    </select>
                    <br><br>
                    <label>Decimal Places:</label>
                    <select name="decimals">
                        <option value="0">0</option>
                        <option value="2" selected>2</option>
                        <option value="4">4</option>
                    </select>
                    <br><br>
                    <label>Position:</label>
                    <select name="position">
                        <option value="1" selected>Before Number</option>
                        <option value="2">After Number</option>
                    </select>
                    <br><br>
                    <label>Spacing:</label>
                    <select name="spacing">
                        <option value="0" selected>No Space</option>
                        <option value="1">With Space</option>
                    </select>
                    <br><br>
                    <input type="submit" name="submit" value="Display Mask">
                </form>
            </div>
        </div>
    </html>
"""

# Result template (without check result) - used for XSS detection
ACCOUNTING_RESULT = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/xss7.css">
            <title>Number Format Wizard - Accounting</title>
        </head>

        <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <div class="box-form">
                    <img class="text-img" src="static/img/logo5_white.png">
                    <h2>Number Format Wizard - Result</h2>
                    <h3>Accounting Format</h3>
                    <br>
                    <div class="result-box">
                        <p><strong>Input:</strong> {number}</p>
                        <p><strong>Currency:</strong> {currency}</p>
                        <p><strong>Decimals:</strong> {decimals}</p>
                        <p><strong>Formatted Result:</strong> {formatted}</p>
                    </div>
                </div>
            </div>
        </div>
    </html>
"""

# Result template with check result - shown to user
ACCOUNTING_RESULT_WITH_CHECK = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/xss7.css">
            <title>Number Format Wizard - Accounting</title>
        </head>

        <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <div class="box-form">
                    <img class="text-img" src="static/img/logo5_white.png">
                    <h2>Number Format Wizard - Result</h2>
                    <h3>Accounting Format</h3>
                    <br>
                    <div class="result-box">
                        <p><strong>Input:</strong> {number}</p>
                        <p><strong>Currency:</strong> {currency}</p>
                        <p><strong>Decimals:</strong> {decimals}</p>
                        <p><strong>Formatted Result:</strong> {formatted}</p>
                    </div>
                    {result}
                    <br>
                    <a href="/samples/Wizards/NumberFormat/Accounting">Try Again</a>
                </div>
            </div>
        </div>
    </html>
"""
