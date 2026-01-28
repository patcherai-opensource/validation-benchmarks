# EduBlocks Learning Platform - Constants and Templates

INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>EduBlocks - Interactive Learning Platform</title>
    <link rel="stylesheet" type="text/css" href="static/css/style.css">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; }
        .header { background: #0f3460; padding: 20px; color: white; text-align: center; }
        .nav { background: #16213e; padding: 10px; text-align: center; }
        .nav a { color: #e94560; text-decoration: none; margin: 0 15px; font-weight: bold; }
        .nav a:hover { color: #fff; }
        .container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
        .hero { text-align: center; color: white; padding: 60px 20px; }
        .hero h1 { font-size: 3em; margin-bottom: 20px; }
        .hero p { font-size: 1.2em; color: #ccc; }
        .features { display: flex; flex-wrap: wrap; justify-content: center; gap: 30px; margin-top: 40px; }
        .feature-card { background: #1a1a2e; border: 1px solid #e94560; border-radius: 10px; padding: 30px; width: 280px; text-align: center; color: white; }
        .feature-card h3 { color: #e94560; }
        .btn { display: inline-block; background: #e94560; color: white; padding: 12px 30px; border-radius: 5px; text-decoration: none; margin-top: 20px; }
        .btn:hover { background: #c73e54; }
        .footer { text-align: center; padding: 20px; color: #666; margin-top: 40px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>EduBlocks</h1>
        <p>Interactive Learning Platform</p>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/courses">Courses</a>
        <a href="/about">About</a>
        <a href="/help">Help</a>
        <a href="/login">Instructor Login</a>
    </div>
    <div class="hero">
        <h1>Learn by Doing</h1>
        <p>Interactive drag-and-drop exercises to master any subject</p>
        <a href="/courses" class="btn">Browse Courses</a>
    </div>
    <div class="container">
        <div class="features">
            <div class="feature-card">
                <h3>Interactive Blocks</h3>
                <p>Drag and drop learning modules designed by expert instructors</p>
            </div>
            <div class="feature-card">
                <h3>Progress Tracking</h3>
                <p>Monitor your learning journey with detailed analytics</p>
            </div>
            <div class="feature-card">
                <h3>Custom Content</h3>
                <p>Instructors can create rich, customized learning experiences</p>
            </div>
        </div>
    </div>
    <div class="footer">
        <p>&copy; 2024 EduBlocks Learning Platform v2.1.4</p>
    </div>
</body>
</html>
"""

ABOUT_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>About - EduBlocks</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; }
        .header { background: #0f3460; padding: 20px; color: white; text-align: center; }
        .nav { background: #16213e; padding: 10px; text-align: center; }
        .nav a { color: #e94560; text-decoration: none; margin: 0 15px; font-weight: bold; }
        .container { max-width: 800px; margin: 0 auto; padding: 40px 20px; color: white; }
        .container h2 { color: #e94560; }
    </style>
</head>
<body>
    <div class="header">
        <h1>EduBlocks</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/courses">Courses</a>
        <a href="/about">About</a>
        <a href="/help">Help</a>
        <a href="/login">Instructor Login</a>
    </div>
    <div class="container">
        <h2>About EduBlocks</h2>
        <p>EduBlocks is an interactive learning platform inspired by the Open edX XBlock framework. Our drag-and-drop modules allow instructors to create engaging learning experiences.</p>
        <h2>Features</h2>
        <ul>
            <li>Custom block creation for instructors</li>
            <li>Rich text support in course content</li>
            <li>Interactive drag-and-drop zones</li>
            <li>Real-time progress tracking</li>
        </ul>
        <h2>Technology</h2>
        <p>Built with Python Flask backend and modern JavaScript frontend.</p>
    </div>
</body>
</html>
"""

COURSES_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Courses - EduBlocks</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; }
        .header { background: #0f3460; padding: 20px; color: white; text-align: center; }
        .nav { background: #16213e; padding: 10px; text-align: center; }
        .nav a { color: #e94560; text-decoration: none; margin: 0 15px; font-weight: bold; }
        .container { max-width: 1000px; margin: 0 auto; padding: 40px 20px; }
        .course-card { background: #1a1a2e; border: 1px solid #e94560; border-radius: 10px; padding: 20px; margin: 20px 0; color: white; }
        .course-card h3 { color: #e94560; margin-top: 0; }
        .btn { display: inline-block; background: #e94560; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; }
    </style>
</head>
<body>
    <div class="header">
        <h1>EduBlocks</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/courses">Courses</a>
        <a href="/about">About</a>
        <a href="/help">Help</a>
        <a href="/login">Instructor Login</a>
    </div>
    <div class="container">
        <h2 style="color: white;">Available Courses</h2>
        <div class="course-card">
            <h3>Introduction to Programming</h3>
            <p>Learn programming basics with interactive drag-and-drop exercises.</p>
            <a href="/learn/intro-101" class="btn">Start Learning</a>
        </div>
        <div class="course-card">
            <h3>Web Development Fundamentals</h3>
            <p>Coming Soon - HTML, CSS, and JavaScript basics.</p>
            <span class="btn" style="background: #666;">Coming Soon</span>
        </div>
    </div>
</body>
</html>
"""

STUDIO_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Instructor Studio - EduBlocks</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #0a0a15; min-height: 100vh; }
        .header { background: #0f3460; padding: 20px; color: white; text-align: center; }
        .nav { background: #16213e; padding: 10px; text-align: center; }
        .nav a { color: #e94560; text-decoration: none; margin: 0 15px; font-weight: bold; }
        .container { max-width: 1000px; margin: 0 auto; padding: 40px 20px; color: white; }
        .dashboard-card { background: #1a1a2e; border: 1px solid #333; border-radius: 10px; padding: 20px; margin: 20px 0; }
        .dashboard-card h3 { color: #e94560; }
        .btn { display: inline-block; background: #e94560; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; margin-right: 10px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>EduBlocks Studio</h1>
        <p>Course Authoring Interface</p>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/studio">Dashboard</a>
        <a href="/studio/blocks">My Blocks</a>
        <a href="/help">Help</a>
    </div>
    <div class="container">
        <h2>Welcome, Instructor!</h2>
        <div class="dashboard-card">
            <h3>Quick Actions</h3>
            <a href="/studio/blocks" class="btn">Manage Blocks</a>
            <a href="/courses" class="btn">Preview Courses</a>
        </div>
        <div class="dashboard-card">
            <h3>Recent Activity</h3>
            <p>Block "Welcome Module" updated - 2 hours ago</p>
            <p>New enrollment in "Introduction to Programming" - 5 hours ago</p>
        </div>
        <div class="dashboard-card">
            <h3>Documentation</h3>
            <p>Blocks support rich HTML content for zone titles and display names. Use the editor to customize your learning materials with formatted text and styling.</p>
        </div>
    </div>
</body>
</html>
"""

STUDIO_BLOCKS_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>My Blocks - EduBlocks Studio</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #0a0a15; min-height: 100vh; }}
        .header {{ background: #0f3460; padding: 20px; color: white; text-align: center; }}
        .nav {{ background: #16213e; padding: 10px; text-align: center; }}
        .nav a {{ color: #e94560; text-decoration: none; margin: 0 15px; font-weight: bold; }}
        .container {{ max-width: 1000px; margin: 0 auto; padding: 40px 20px; color: white; }}
        .block-item {{ background: #1a1a2e; border: 1px solid #333; border-radius: 5px; padding: 15px; margin: 10px 0; }}
        .block-item a {{ color: #e94560; text-decoration: none; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>EduBlocks Studio</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/studio">Dashboard</a>
        <a href="/studio/blocks">My Blocks</a>
        <a href="/help">Help</a>
    </div>
    <div class="container">
        <h2>My Learning Blocks</h2>
        {0}
    </div>
</body>
</html>
"""

EDIT_BLOCK_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Edit Block - EduBlocks Studio</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #0a0a15; min-height: 100vh; }}
        .header {{ background: #0f3460; padding: 20px; color: white; text-align: center; }}
        .nav {{ background: #16213e; padding: 10px; text-align: center; }}
        .nav a {{ color: #e94560; text-decoration: none; margin: 0 15px; font-weight: bold; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 40px 20px; color: white; }}
        .form-group {{ margin: 20px 0; }}
        .form-group label {{ display: block; margin-bottom: 5px; color: #e94560; font-weight: bold; }}
        .form-group input, .form-group textarea {{ width: 100%; padding: 10px; border: 1px solid #333; border-radius: 5px; background: #1a1a2e; color: white; box-sizing: border-box; }}
        .form-group small {{ color: #888; }}
        .btn {{ background: #e94560; color: white; padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }}
        .btn:hover {{ background: #c73e54; }}
        .section {{ background: #1a1a2e; border: 1px solid #333; border-radius: 10px; padding: 20px; margin: 20px 0; }}
        .section h3 {{ color: #e94560; margin-top: 0; }}
        .preview-link {{ color: #e94560; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>EduBlocks Studio</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/studio">Dashboard</a>
        <a href="/studio/blocks">My Blocks</a>
        <a href="/help">Help</a>
    </div>
    <div class="container">
        <h2>Edit Block: {block_id}</h2>
        <p><a href="/learn/{block_id}" class="preview-link">Preview this block as student &rarr;</a></p>
        
        <div class="section">
            <h3>Basic Information</h3>
            <form method="POST">
                <div class="form-group">
                    <label>Course Name</label>
                    <input type="text" name="course_name" value="{course_name}">
                    <small>Plain text only - HTML will be sanitized</small>
                </div>
                <button type="submit" class="btn">Update Course Name</button>
            </form>
        </div>
        
        <div class="section">
            <h3>Display Settings</h3>
            <form method="POST">
                <div class="form-group">
                    <label>Display Name (Block Title)</label>
                    <input type="text" name="display_name" value="{display_name}">
                    <small>Supports HTML formatting for rich titles</small>
                </div>
                <button type="submit" class="btn">Update Display Name</button>
            </form>
        </div>
        
        <div class="section">
            <h3>Question Content</h3>
            <form method="POST">
                <div class="form-group">
                    <label>Question Text</label>
                    <textarea name="question_text" rows="3">{question_text}</textarea>
                    <small>Plain text only - HTML will be sanitized</small>
                </div>
                <button type="submit" class="btn">Update Question</button>
            </form>
        </div>
        
        <div class="section">
            <h3>Drop Zones</h3>
            <form method="POST">
                <input type="hidden" name="zone_index" value="0">
                <div class="form-group">
                    <label>Zone 1 Title</label>
                    <input type="text" name="zone_title" value="{zone0_title}">
                    <small>Rich content supported for zone customization</small>
                </div>
                <button type="submit" class="btn">Update Zone 1</button>
            </form>
            <form method="POST" style="margin-top: 15px;">
                <input type="hidden" name="zone_index" value="1">
                <div class="form-group">
                    <label>Zone 2 Title</label>
                    <input type="text" name="zone_title" value="{zone1_title}">
                    <small>Rich content supported for zone customization</small>
                </div>
                <button type="submit" class="btn">Update Zone 2</button>
            </form>
        </div>
        
        <div class="section">
            <h3>Draggable Items</h3>
            <form method="POST">
                <input type="hidden" name="item_index" value="0">
                <div class="form-group">
                    <label>Item 1 Name</label>
                    <input type="text" name="item_name" value="{item0_name}">
                    <small>Plain text only - HTML will be sanitized</small>
                </div>
                <button type="submit" class="btn">Update Item 1</button>
            </form>
            <form method="POST" style="margin-top: 15px;">
                <input type="hidden" name="item_index" value="1">
                <div class="form-group">
                    <label>Item 2 Name</label>
                    <input type="text" name="item_name" value="{item1_name}">
                    <small>Plain text only - HTML will be sanitized</small>
                </div>
                <button type="submit" class="btn">Update Item 2</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

STUDENT_VIEW_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{course_name} - EduBlocks</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; }}
        .header {{ background: #0f3460; padding: 20px; color: white; text-align: center; }}
        .nav {{ background: #16213e; padding: 10px; text-align: center; }}
        .nav a {{ color: #e94560; text-decoration: none; margin: 0 15px; font-weight: bold; }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 40px 20px; }}
        .block-title {{ color: #e94560; font-size: 2em; text-align: center; margin-bottom: 10px; }}
        .question {{ background: #1a1a2e; border: 1px solid #333; border-radius: 10px; padding: 20px; margin: 20px 0; color: white; text-align: center; }}
        .zones-container {{ display: flex; gap: 20px; justify-content: center; flex-wrap: wrap; margin: 30px 0; }}
        .drop-zone {{ background: #1a1a2e; border: 2px dashed #e94560; border-radius: 10px; padding: 20px; min-width: 200px; min-height: 150px; text-align: center; }}
        .zone-title {{ color: #e94560; font-weight: bold; margin-bottom: 15px; font-size: 1.2em; }}
        .items-container {{ display: flex; gap: 15px; justify-content: center; flex-wrap: wrap; margin: 30px 0; }}
        .drag-item {{ background: #e94560; color: white; padding: 15px 25px; border-radius: 5px; cursor: grab; font-weight: bold; }}
        .alert {{ padding: 20px; border-radius: 10px; margin: 20px 0; text-align: center; }}
        .alert-success {{ background: #28a745; color: white; font-size: 1.2em; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>EduBlocks</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/courses">Courses</a>
        <a href="/about">About</a>
        <a href="/help">Help</a>
    </div>
    <div class="container">
        <div class="block-title">{display_name}</div>
        <div class="question">
            <p>{question_text}</p>
        </div>
        <div class="zones-container">
            {zones_html}
        </div>
        <div class="items-container">
            {items_html}
        </div>
    </div>
</body>
</html>
"""

HELP_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Help - EduBlocks</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; }
        .header { background: #0f3460; padding: 20px; color: white; text-align: center; }
        .nav { background: #16213e; padding: 10px; text-align: center; }
        .nav a { color: #e94560; text-decoration: none; margin: 0 15px; font-weight: bold; }
        .container { max-width: 800px; margin: 0 auto; padding: 40px 20px; color: white; }
        .faq { background: #1a1a2e; border: 1px solid #333; border-radius: 10px; padding: 20px; margin: 20px 0; }
        .faq h3 { color: #e94560; }
        code { background: #333; padding: 2px 6px; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>EduBlocks Help</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/courses">Courses</a>
        <a href="/about">About</a>
        <a href="/help">Help</a>
        <a href="/login">Instructor Login</a>
    </div>
    <div class="container">
        <h2>Frequently Asked Questions</h2>
        
        <div class="faq">
            <h3>How do I access courses?</h3>
            <p>Browse the <a href="/courses" style="color: #e94560;">Courses</a> page to see available learning modules.</p>
        </div>
        
        <div class="faq">
            <h3>How do instructors create content?</h3>
            <p>Instructors can access the Studio at <code>/studio</code> to manage learning blocks and customize content.</p>
        </div>
        
        <div class="faq">
            <h3>What content formats are supported?</h3>
            <p>Block display names and zone titles support rich HTML formatting. Other fields use plain text for security.</p>
        </div>
        
        <div class="faq">
            <h3>API Access</h3>
            <p>Developers can access course data via our API:</p>
            <ul>
                <li><code>GET /api/courses</code> - List all courses</li>
                <li><code>GET /api/block/{id}/data</code> - Get block data</li>
                <li><code>GET /api/health</code> - Health check</li>
            </ul>
        </div>
        
        <div class="faq">
            <h3>Feedback</h3>
            <p>Have suggestions? Visit our <a href="/feedback" style="color: #e94560;">feedback page</a>.</p>
        </div>
    </div>
</body>
</html>
"""

LOGIN_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Instructor Login - EduBlocks</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; display: flex; flex-direction: column; }
        .header { background: #0f3460; padding: 20px; color: white; text-align: center; }
        .nav { background: #16213e; padding: 10px; text-align: center; }
        .nav a { color: #e94560; text-decoration: none; margin: 0 15px; font-weight: bold; }
        .login-container { flex: 1; display: flex; align-items: center; justify-content: center; }
        .login-box { background: #1a1a2e; border: 1px solid #e94560; border-radius: 10px; padding: 40px; width: 350px; }
        .login-box h2 { color: #e94560; text-align: center; margin-bottom: 30px; }
        .form-group { margin: 20px 0; }
        .form-group label { display: block; color: white; margin-bottom: 5px; }
        .form-group input { width: 100%; padding: 12px; border: 1px solid #333; border-radius: 5px; background: #16213e; color: white; box-sizing: border-box; }
        .btn { width: 100%; background: #e94560; color: white; padding: 12px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        .info { color: #888; font-size: 0.9em; text-align: center; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>EduBlocks</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/courses">Courses</a>
        <a href="/about">About</a>
        <a href="/help">Help</a>
    </div>
    <div class="login-container">
        <div class="login-box">
            <h2>Instructor Login</h2>
            <form method="POST">
                <div class="form-group">
                    <label>Username</label>
                    <input type="text" name="username" placeholder="Enter username">
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" name="password" placeholder="Enter password">
                </div>
                <button type="submit" class="btn">Login</button>
            </form>
            <p class="info">Contact admin for instructor access</p>
        </div>
    </div>
</body>
</html>
"""

FEEDBACK_FORM = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Feedback - EduBlocks</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; }
        .header { background: #0f3460; padding: 20px; color: white; text-align: center; }
        .nav { background: #16213e; padding: 10px; text-align: center; }
        .nav a { color: #e94560; text-decoration: none; margin: 0 15px; font-weight: bold; }
        .container { max-width: 600px; margin: 0 auto; padding: 40px 20px; }
        .form-box { background: #1a1a2e; border: 1px solid #333; border-radius: 10px; padding: 30px; }
        .form-box h2 { color: #e94560; }
        .form-group { margin: 20px 0; }
        .form-group textarea { width: 100%; padding: 12px; border: 1px solid #333; border-radius: 5px; background: #16213e; color: white; box-sizing: border-box; }
        .btn { background: #e94560; color: white; padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="header">
        <h1>EduBlocks</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/courses">Courses</a>
        <a href="/about">About</a>
        <a href="/help">Help</a>
    </div>
    <div class="container">
        <div class="form-box">
            <h2>Submit Feedback</h2>
            <form method="POST">
                <div class="form-group">
                    <textarea name="feedback" rows="6" placeholder="Enter your feedback here..."></textarea>
                </div>
                <button type="submit" class="btn">Submit</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

FEEDBACK_RESPONSE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Feedback Received - EduBlocks</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; }}
        .header {{ background: #0f3460; padding: 20px; color: white; text-align: center; }}
        .nav {{ background: #16213e; padding: 10px; text-align: center; }}
        .nav a {{ color: #e94560; text-decoration: none; margin: 0 15px; font-weight: bold; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; text-align: center; color: white; }}
        .success {{ background: #28a745; padding: 20px; border-radius: 10px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>EduBlocks</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/courses">Courses</a>
        <a href="/about">About</a>
        <a href="/help">Help</a>
    </div>
    <div class="container">
        <div class="success">
            <h2>Thank you for your feedback!</h2>
            <p>Your message: {0}</p>
        </div>
        <a href="/" style="color: #e94560;">Return to Home</a>
    </div>
</body>
</html>
"""

# Image routes for XSS checking (kept for compatibility)
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
