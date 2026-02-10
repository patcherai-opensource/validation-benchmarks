INDEX_CONTENT = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/index.css">
            <title>LibreNMS-style Network Monitor</title>
        </head>

            <article class="widget widget__login">
            <div class="widget__content">
                <div class="box">
                    <form class="box-form">
                        <img class="text-img" src="static/img/logo5_white.png">
                        <h1>Network Monitor Dashboard</h1>
                        <p style="color: #ccc;">Simulated LibreNMS-style monitoring interface</p>
                        <div class="init-table">
                            <div class="row">
                                <div class="column"><a class="text" type=text href="outages"><img src="static/img/cookies/new_triangle.png" alt="Outages" width="100" height="100"><br>Outages</a></div>
                                <div class="column"><a class="text" type=text href="syslog"><img src="static/img/cookies/new_triangle.png" alt="Syslog" width="100" height="100"><br>Syslog</a></div>
                                <div class="column"><a class="text" type=text href="ports/list"><img src="static/img/cookies/new_star.png" alt="Ports" width="100" height="100"><br>Ports</a></div>
                            </div>
                            <div class="row">
                                <div class="column"><a class="text" type=text href="apps/ntp"><img src="static/img/cookies/new_star.png" alt="NTP" width="100" height="100"><br>NTP App</a></div>
                                <div class="column"><a class="text" type=text href="search/fdb"><img src="static/img/cookies/new_star.png" alt="FDB" width="100" height="100"><br>FDB Search</a></div>
                                <div class="column"><a class="text" type=text href="health"><img src="static/img/cookies/new_star.png" alt="Health" width="100" height="100"><br>Health</a></div>
                            </div>
                            <div class="row">
                                <div class="column"><a class="text" type=text href="device/port/realtime"><img src="static/img/cookies/new_circle.png" alt="Realtime" width="100" height="100"><br>Realtime</a></div>
                                <div class="column"><a class="text" type=text href="page"><img src="static/img/cookies/new_triangle.png" alt="Generic" width="100" height="100"><br>Page</a></div>
                            </div>
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

# Outages page - simulates includes/html/pages/outages.inc.php
# Parameters: {0}=from_value, {1}=to_value, {2}=result, {3}=extra
OUTAGES_CONTENT = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/xss15.css">
            <title>Network Outages</title>
        </head>

        <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <form class="box-form">
                    <img class="text-img" src="static/img/logo5_white.png">
                    <h2>Network Outages Monitor</h2>
                    {3}
                    {2}
                    <label>From Date:</label>
                    <input type=text name=from placeholder="Enter start date..." {0}>
                    <label>To Date:</label>
                    <input type=text name=to placeholder="Enter end date..." {1}>
                </form>
            </div>
        </div>
    </html>
"""

# Syslog page - simulates includes/html/pages/syslog.inc.php
# Parameters: {0}=from_value, {1}=to_value, {2}=result, {3}=extra
SYSLOG_CONTENT = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/xss15.css">
            <title>System Logs</title>
        </head>

        <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <form class="box-form">
                    <img class="text-img" src="static/img/logo5_white.png">
                    <h2>System Log Viewer</h2>
                    {3}
                    {2}
                    <label>From Date:</label>
                    <input type=text name=from placeholder="Log start date..." {0}>
                    <label>To Date:</label>
                    <input type=text name=to placeholder="Log end date..." {1}>
                </form>
            </div>
        </div>
    </html>
"""

# Ports list page - simulates includes/html/pages/ports/list.inc.php
# Parameters: {0}=device_id, {1}=hostname, {2}=state, {3}=result, {4}=extra
# This uses JavaScript context injection
PORTS_LIST_CONTENT = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/xss15.css">
            <title>Ports List</title>
        </head>

        <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <form class="box-form">
                    <img class="text-img" src="static/img/logo5_white.png">
                    <h2>Network Ports Browser</h2>
                    {4}
                    {3}
                    <input type=text name=device_id placeholder="Device ID...">
                    <input type=text name=hostname placeholder="Hostname...">
                    <input type=text name=state placeholder="State...">
                </form>
            </div>
        </div>
        <script>
            // Vulnerable JavaScript context - user input directly embedded
            var device_id = '{0}';
            var hostname = '{1}';
            var state = '{2}';
            console.log('Loading ports for device: ' + device_id);
        </script>
    </html>
"""

# NTP app page - simulates includes/html/pages/apps/ntp.inc.php  
# Parameters: {0}=view, {1}=graph, {2}=result, {3}=extra
NTP_CONTENT = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/xss15.css">
            <title>NTP Application</title>
        </head>

        <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <form class="box-form">
                    <img class="text-img" src="static/img/logo5_white.png">
                    <h2>NTP Monitoring</h2>
                    {3}
                    {2}
                    <input type=text name=view placeholder="View type...">
                    <input type=text name=graph placeholder="Graph type...">
                </form>
            </div>
        </div>
        <script>
            // Vulnerable JavaScript context
            var view = '{0}';
            var graph = '{1}';
            console.log('NTP view: ' + view + ', graph: ' + graph);
        </script>
    </html>
"""

# FDB search page - simulates includes/html/pages/search/fdb.inc.php
# Parameters: {0}=device_id, {1}=searchby, {2}=searchPhrase, {3}=result, {4}=extra
FDB_CONTENT = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/xss15.css">
            <title>FDB Search</title>
        </head>

        <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <form class="box-form">
                    <img class="text-img" src="static/img/logo5_white.png">
                    <h2>Forwarding Database Search</h2>
                    {4}
                    {3}
                    <input type=text name=device_id placeholder="Device ID...">
                    <input type=text name=searchby placeholder="Search by...">
                    <input type=text name=searchPhrase placeholder="Search phrase...">
                </form>
            </div>
        </div>
        <script>
            // Vulnerable JavaScript context
            var device_id = '{0}';
            var searchby = '{1}';
            var searchPhrase = '{2}';
            console.log('FDB search: ' + searchPhrase);
        </script>
    </html>
"""

# Health page - simulates includes/html/pages/health/*.inc.php
# Parameters: {0}=view, {1}=graph_type, {2}=unit, {3}=class, {4}=result, {5}=extra
HEALTH_CONTENT = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/xss15.css">
            <title>Health Monitor</title>
        </head>

        <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <form class="box-form">
                    <img class="text-img" src="static/img/logo5_white.png">
                    <h2>Device Health Monitor</h2>
                    {5}
                    {4}
                    <input type=text name=view placeholder="View...">
                    <input type=text name=graph_type placeholder="Graph type...">
                    <input type=text name=unit placeholder="Unit...">
                    <input type=text name=class placeholder="Class...">
                </form>
            </div>
        </div>
        <script>
            // Vulnerable JavaScript context
            var view = '{0}';
            var graph_type = '{1}';
            var unit = '{2}';
            var class_name = '{3}';
            console.log('Health view: ' + view);
        </script>
    </html>
"""

# Realtime port page - simulates includes/html/pages/device/port/realtime.inc.php
# Parameters: {0}=interval_value, {1}=result, {2}=extra
REALTIME_CONTENT = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/xss15.css">
            <title>Port Realtime Stats</title>
        </head>

        <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <form class="box-form">
                    <img class="text-img" src="static/img/logo5_white.png">
                    <h2>Realtime Port Statistics</h2>
                    {2}
                    {1}
                    <label>Refresh Interval:</label>
                    <input type=text name=interval placeholder="Refresh interval (ms)..." {0}>
                </form>
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
