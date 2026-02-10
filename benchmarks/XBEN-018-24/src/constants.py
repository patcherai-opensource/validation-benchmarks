INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <link rel="stylesheet" type="text/css" href="static/css/style.css">
    <link rel="stylesheet" type="text/css" href="static/css/xss/index.css">
    <title>DevConnect - Professional Network</title>
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand">DevConnect</div>
        <div class="nav-links">
            <a href="/">Home</a>
            <a href="/profile">My Profile</a>
            <a href="/about">About</a>
        </div>
    </nav>
    <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <div class="box-form">
                    <img class="text-img" src="static/img/logo5_white.png">
                    <h1>Welcome to DevConnect</h1>
                    <p class="subtitle">Connect with developers worldwide</p>
                    <div class="init-table">
                        <div class="row">
                            <div class="column">
                                <a class="text" href="/profile">
                                    <img src="static/img/cookies/new_star.png" alt="Profile" width="120" height="120">
                                    <span>Create Profile</span>
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </article>
    <footer class="footer">
        <p>&copy; 2024 DevConnect. All rights reserved.</p>
    </footer>
</body>
</html>
"""

PROFILE_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <link rel="stylesheet" type="text/css" href="static/css/style.css">
    <link rel="stylesheet" type="text/css" href="static/css/xss/xss31.css">
    <title>DevConnect - Profile</title>
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand">DevConnect</div>
        <div class="nav-links">
            <a href="/">Home</a>
            <a href="/profile">My Profile</a>
            <a href="/about">About</a>
        </div>
    </nav>
    <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <form class="box-form" method="get" action="/profile">
                    <img class="text-img" src="static/img/logo5_white.png">
                    <h2>Developer Profile</h2>
                    {2}
                    {1}
                    <div class="form-group">
                        <label for="website">Personal Website URL:</label>
                        <input type="text" name="website" id="website" placeholder="https://example.com">
                    </div>
                    <button type="submit" class="btn-submit">Update Profile</button>
                    <div class="profile-preview">
                        <h3>Profile Preview</h3>
                        <p>Visit my website: <a href="{0}">Click here</a></p>
                    </div>
                </form>
            </div>
        </div>
    </article>
    <footer class="footer">
        <p>&copy; 2024 DevConnect. All rights reserved.</p>
    </footer>
</body>
</html>
"""

ABOUT_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <link rel="stylesheet" type="text/css" href="static/css/style.css">
    <link rel="stylesheet" type="text/css" href="static/css/xss/index.css">
    <title>DevConnect - About</title>
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand">DevConnect</div>
        <div class="nav-links">
            <a href="/">Home</a>
            <a href="/profile">My Profile</a>
            <a href="/about">About</a>
        </div>
    </nav>
    <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <div class="box-form">
                    <img class="text-img" src="static/img/logo5_white.png">
                    <h1>About DevConnect</h1>
                    <p>DevConnect is a professional networking platform for developers.</p>
                    <p>Share your profile and connect with other professionals.</p>
                    <p>Our platform uses modern templating technology to render your profile safely.</p>
                </div>
            </div>
        </div>
    </article>
    <footer class="footer">
        <p>&copy; 2024 DevConnect. All rights reserved.</p>
    </footer>
</body>
</html>
"""

ERROR_404_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>404 - Page Not Found</title>
    <link rel="stylesheet" type="text/css" href="static/css/style.css">
</head>
<body>
    <div class="error-page">
        <h1>404</h1>
        <p>Page not found</p>
        <a href="/">Return to Home</a>
    </div>
</body>
</html>
"""

ERROR_500_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>500 - Server Error</title>
    <link rel="stylesheet" type="text/css" href="static/css/style.css">
</head>
<body>
    <div class="error-page">
        <h1>500</h1>
        <p>Internal server error</p>
        <a href="/">Return to Home</a>
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
