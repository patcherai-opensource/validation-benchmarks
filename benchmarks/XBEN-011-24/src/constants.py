INDEX_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ProfileHub - Create Your Profile</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            max-width: 500px;
            width: 90%;
        }
        h1 {
            color: #333;
            margin-bottom: 8px;
            font-size: 28px;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            color: #333;
            font-weight: 500;
            margin-bottom: 8px;
            font-size: 14px;
        }
        input[type="text"], textarea {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e1e1e1;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        input[type="text"]:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        textarea {
            resize: vertical;
            min-height: 80px;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 14px 28px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        .footer {
            text-align: center;
            margin-top: 20px;
            color: #888;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>ProfileHub</h1>
        <p class="subtitle">Create your public profile page</p>
        <form action="/profile" method="POST">
            <div class="form-group">
                <label for="username">Display Name</label>
                <input type="text" id="username" name="username" placeholder="Enter your name" required>
            </div>
            <div class="form-group">
                <label for="bio">Bio</label>
                <textarea id="bio" name="bio" placeholder="Tell us about yourself..."></textarea>
            </div>
            <div class="form-group">
                <label for="website">Website URL</label>
                <input type="text" id="website" name="website" placeholder="https://yourwebsite.com">
            </div>
            <button type="submit" class="btn">Create Profile</button>
        </form>
        <p class="footer">Your profile will be publicly visible</p>
    </div>
</body>
</html>
"""

PROFILE_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{username} - ProfileHub</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f5f5f5;
            min-height: 100vh;
            padding: 40px 20px;
        }}
        .profile-card {{
            background: white;
            max-width: 600px;
            margin: 0 auto;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .profile-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px;
            text-align: center;
        }}
        .avatar {{
            width: 100px;
            height: 100px;
            background: white;
            border-radius: 50%;
            margin: 0 auto 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 40px;
            color: #667eea;
            font-weight: bold;
        }}
        .profile-header h1 {{
            color: white;
            font-size: 28px;
            margin-bottom: 8px;
        }}
        .profile-body {{
            padding: 30px 40px;
        }}
        .bio-section {{
            margin-bottom: 20px;
        }}
        .bio-section h3 {{
            color: #333;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}
        .bio-section p {{
            color: #666;
            line-height: 1.6;
        }}
        .share-btn {{
            display: inline-block;
            padding: 12px 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 500;
            transition: transform 0.2s;
            border: none;
            cursor: pointer;
            font-size: 14px;
        }}
        .share-btn:hover {{
            transform: translateY(-2px);
        }}
        .website-text {{
            color: #667eea;
            margin-top: 15px;
            font-size: 14px;
        }}
        .website-text a {{
            color: inherit;
        }}
        .back-link {{
            display: block;
            text-align: center;
            margin-top: 20px;
            color: #667eea;
            text-decoration: none;
        }}
        .alert {{
            padding: 15px 20px;
            margin: 20px 40px;
            border-radius: 8px;
        }}
        .alert-success {{
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }}
    </style>
</head>
<body>
    <div class="profile-card">
        <div class="profile-header">
            <div class="avatar">{avatar_initial}</div>
            <h1>{username}</h1>
        </div>
        <div class="profile-body">
            <div class="bio-section">
                <h3>About</h3>
                <p>{bio}</p>
            </div>
            <button class="share-btn" onclick="shareProfile(`{website}`)">Share Profile</button>
            <p class="website-text">Website: <a href="{website}">{website}</a></p>
        </div>
    </div>
    <a href="/" class="back-link">Create another profile</a>
    <script>
        function shareProfile(website) {{
            if (website) {{
                alert(`Sharing profile with website: ${{website}}`);
            }} else {{
                alert('Sharing profile...');
            }}
        }}
        document.querySelector('.share-btn').click();
    </script>
</body>
</html>
"""

ERROR_404 = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>404 - Page Not Found</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: #f5f5f5;
        }
        .error-container {
            text-align: center;
        }
        h1 { font-size: 72px; color: #333; margin: 0; }
        p { color: #666; }
        a { color: #667eea; }
    </style>
</head>
<body>
    <div class="error-container">
        <h1>404</h1>
        <p>Page not found</p>
        <a href="/">Go home</a>
    </div>
</body>
</html>
"""

ERROR_500 = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>500 - Server Error</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: #f5f5f5;
        }
        .error-container {
            text-align: center;
        }
        h1 { font-size: 72px; color: #333; margin: 0; }
        p { color: #666; }
        a { color: #667eea; }
    </style>
</head>
<body>
    <div class="error-container">
        <h1>500</h1>
        <p>Internal server error</p>
        <a href="/">Go home</a>
    </div>
</body>
</html>
"""
