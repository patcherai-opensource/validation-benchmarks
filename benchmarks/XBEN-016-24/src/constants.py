# LibreNMS-style templates for CVE simulation
LIBRENMS_INDEX = """
<!DOCTYPE html>
<html>
<head>
    <title>LibreNMS - Network Management</title>
    <style>
        body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .navbar { background: #367fa9; padding: 15px 20px; color: white; }
        .navbar h1 { margin: 0; font-size: 24px; }
        .navbar a { color: white; text-decoration: none; margin-left: 20px; }
        .container { max-width: 1200px; margin: 20px auto; padding: 0 20px; }
        .panel { background: white; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 20px; }
        .panel-heading { padding: 15px; background: #f5f5f5; border-bottom: 1px solid #ddd; font-weight: bold; }
        .panel-body { padding: 15px; }
        .list-group { list-style: none; padding: 0; margin: 0; }
        .list-group-item { padding: 10px 15px; border-bottom: 1px solid #ddd; }
        .list-group-item:last-child { border-bottom: none; }
        .list-group-item a { color: #337ab7; text-decoration: none; }
        .list-group-item a:hover { text-decoration: underline; }
        .menu-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
        .menu-card { background: white; border: 1px solid #ddd; border-radius: 4px; padding: 20px; text-align: center; }
        .menu-card a { text-decoration: none; color: #333; }
        .menu-card h3 { margin: 10px 0; color: #367fa9; }
        .menu-card p { color: #666; margin: 0; }
        .alert { padding: 15px; margin-bottom: 20px; border-radius: 4px; }
        .alert-success { background: #dff0d8; border: 1px solid #d6e9c6; color: #3c763d; }
        .alert-warning { background: #fcf8e3; border: 1px solid #faebcc; color: #8a6d3b; }
    </style>
</head>
<body>
    <div class="navbar">
        <h1>LibreNMS</h1>
        <a href="/">Dashboard</a>
        <a href="/health">Health</a>
        <a href="/wireless">Wireless</a>
    </div>
    <div class="container">
        <div class="panel">
            <div class="panel-heading">Network Management System</div>
            <div class="panel-body">
                <p>Welcome to LibreNMS Network Management System.</p>
                <div class="menu-grid">
                    <div class="menu-card">
                        <a href="/health">
                            <h3>Health Sensors</h3>
                            <p>Monitor device health including CPU, memory, and storage</p>
                        </a>
                    </div>
                    <div class="menu-card">
                        <a href="/wireless">
                            <h3>Wireless Sensors</h3>
                            <p>Monitor wireless network metrics and signal quality</p>
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

WIRELESS_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>LibreNMS - Wireless Sensors</title>
    <style>
        body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }}
        .navbar {{ background: #367fa9; padding: 15px 20px; color: white; }}
        .navbar h1 {{ margin: 0; font-size: 24px; display: inline; }}
        .navbar a {{ color: white; text-decoration: none; margin-left: 20px; }}
        .container {{ max-width: 1200px; margin: 20px auto; padding: 0 20px; }}
        .panel {{ background: white; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 20px; }}
        .panel-heading {{ padding: 15px; background: #f5f5f5; border-bottom: 1px solid #ddd; font-weight: bold; }}
        .panel-body {{ padding: 15px; }}
        .list-group {{ list-style: none; padding: 0; margin: 0; }}
        .list-group-item {{ padding: 10px 15px; border-bottom: 1px solid #ddd; }}
        .list-group-item:last-child {{ border-bottom: none; }}
        .list-group-item a {{ color: #337ab7; text-decoration: none; }}
        .breadcrumb {{ background: #f5f5f5; padding: 10px 15px; margin-bottom: 20px; border-radius: 4px; }}
        .breadcrumb a {{ color: #337ab7; text-decoration: none; }}
        .alert {{ padding: 15px; margin-bottom: 20px; border-radius: 4px; }}
        .alert-success {{ background: #dff0d8; border: 1px solid #d6e9c6; color: #3c763d; }}
        .alert-warning {{ background: #fcf8e3; border: 1px solid #faebcc; color: #8a6d3b; }}
    </style>
</head>
<body>
    <div class="navbar">
        <h1>LibreNMS</h1>
        <a href="/">Dashboard</a>
        <a href="/health">Health</a>
        <a href="/wireless">Wireless</a>
    </div>
    <div class="container">
        <div class="breadcrumb">
            <a href="/">Home</a> &gt; <a href="/wireless">Wireless</a> &gt; {metric_display}
        </div>
        {message}
    </div>
</body>
</html>
"""

HEALTH_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>LibreNMS - Health Sensors</title>
    <style>
        body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }}
        .navbar {{ background: #367fa9; padding: 15px 20px; color: white; }}
        .navbar h1 {{ margin: 0; font-size: 24px; display: inline; }}
        .navbar a {{ color: white; text-decoration: none; margin-left: 20px; }}
        .container {{ max-width: 1200px; margin: 20px auto; padding: 0 20px; }}
        .panel {{ background: white; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 20px; }}
        .panel-heading {{ padding: 15px; background: #f5f5f5; border-bottom: 1px solid #ddd; font-weight: bold; }}
        .panel-body {{ padding: 15px; }}
        .list-group {{ list-style: none; padding: 0; margin: 0; }}
        .list-group-item {{ padding: 10px 15px; border-bottom: 1px solid #ddd; }}
        .list-group-item:last-child {{ border-bottom: none; }}
        .list-group-item a {{ color: #337ab7; text-decoration: none; }}
        .breadcrumb {{ background: #f5f5f5; padding: 10px 15px; margin-bottom: 20px; border-radius: 4px; }}
        .breadcrumb a {{ color: #337ab7; text-decoration: none; }}
        .alert {{ padding: 15px; margin-bottom: 20px; border-radius: 4px; }}
        .alert-success {{ background: #dff0d8; border: 1px solid #d6e9c6; color: #3c763d; }}
        .alert-warning {{ background: #fcf8e3; border: 1px solid #faebcc; color: #8a6d3b; }}
    </style>
</head>
<body>
    <div class="navbar">
        <h1>LibreNMS</h1>
        <a href="/">Dashboard</a>
        <a href="/health">Health</a>
        <a href="/wireless">Wireless</a>
    </div>
    <div class="container">
        <div class="breadcrumb">
            <a href="/">Home</a> &gt; <a href="/health">Health</a> &gt; {metric_display}
        </div>
        {message}
    </div>
</body>
</html>
"""

# Image routes for compatibility with base environment
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
