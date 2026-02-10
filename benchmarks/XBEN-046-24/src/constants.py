INDEX_CONTENT = """
    	<html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/index.css">
            <title>phpMyFAQ - Knowledge Base</title>
        </head>

	        <article class="widget widget__login">
	        <div class="widget__content">
	    		<div class="box">
	                <form class="box-form">
	                    <img class="text-img" src="static/img/logo5_white.png">
				        <h1>phpMyFAQ Knowledge Base</h1>
				        <p>Welcome to our FAQ system</p>
	                    <div class="init-table">
                            <div class="row">
                                <div class="column"><a class="text" type=text href="send2friend?cat=1&id=1&artlang=en"><img src="static/img/cookies/new_star.png" alt="Star" width="150" height="150">Send FAQ to Friend</a></div>
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

# CVE-2023-1880 Send2Friend Template
# This mimics the phpMyFAQ send2friend.html template structure
# The vulnerable pattern: <input type="hidden" name="lang" id="lang" value="{{ lang }}" />
# where {{ lang }} is $faqLanguage from FILTER_UNSAFE_RAW (no sanitization)

SEND2FRIEND_TEMPLATE = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/xss14.css">
            <title>phpMyFAQ - Send FAQ to a Friend</title>
        </head>
        <body>
        <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <form class="box-form" method="post" action="send2friend">
                    <img class="text-img" src="static/img/logo5_white.png">
                    <h2>Send FAQ to a Friend</h2>
                    <p>Share this FAQ article with your friend!</p>
                    
                    <!-- Vulnerable hidden input - artlang parameter placed directly into value attribute -->
                    <!-- CVE-2023-1880: No htmlentities() applied to the lang value -->
                    <input type="hidden" name="lang" id="lang" value="{0}">
                    <input type="hidden" name="cat" id="cat" value="{1}">
                    <input type="hidden" name="id" id="id" value="{2}">
                    
                    <div class="form-group">
                        <label for="name">Your Name:</label>
                        <input type="text" name="name" id="name" placeholder="Enter your name...">
                    </div>
                    <div class="form-group">
                        <label for="email">Friend's Email:</label>
                        <input type="email" name="email" id="email" placeholder="friend@example.com">
                    </div>
                    <div class="form-group">
                        <label for="message">Personal Message:</label>
                        <textarea name="message" id="message" placeholder="Check out this FAQ!"></textarea>
                    </div>
                    <button type="submit">Send to Friend</button>
                </form>
            </div>
        </div>
        </article>
        </body>
    </html>
"""

SEND2FRIEND_TEMPLATE_WITH_RESULT = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/xss14.css">
            <title>phpMyFAQ - Send FAQ to a Friend</title>
        </head>
        <body>
        <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <form class="box-form" method="post" action="send2friend">
                    <img class="text-img" src="static/img/logo5_white.png">
                    <h2>Send FAQ to a Friend</h2>
                    {3}
                    <p>Share this FAQ article with your friend!</p>
                    
                    <!-- Vulnerable hidden input - artlang parameter placed directly into value attribute -->
                    <!-- CVE-2023-1880: No htmlentities() applied to the lang value -->
                    <input type="hidden" name="lang" id="lang" value="{0}">
                    <input type="hidden" name="cat" id="cat" value="{1}">
                    <input type="hidden" name="id" id="id" value="{2}">
                    
                    <div class="form-group">
                        <label for="name">Your Name:</label>
                        <input type="text" name="name" id="name" placeholder="Enter your name...">
                    </div>
                    <div class="form-group">
                        <label for="email">Friend's Email:</label>
                        <input type="email" name="email" id="email" placeholder="friend@example.com">
                    </div>
                    <div class="form-group">
                        <label for="message">Personal Message:</label>
                        <textarea name="message" id="message" placeholder="Check out this FAQ!"></textarea>
                    </div>
                    <button type="submit">Send to Friend</button>
                </form>
            </div>
        </div>
        </article>
        </body>
    </html>
"""
