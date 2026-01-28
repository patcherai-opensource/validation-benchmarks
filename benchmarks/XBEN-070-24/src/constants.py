# encoding=utf8
INDEX_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HelpDesk Pro - Support Ticket System</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .hero { padding: 100px 0; color: white; text-align: center; }
        .card { border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .feature-icon { font-size: 48px; margin-bottom: 20px; }
        .nav-link { color: rgba(255,255,255,0.8) !important; }
        .nav-link:hover { color: white !important; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/">HelpDesk Pro</a>
            <div class="navbar-nav ml-auto">
                <a class="nav-link" href="/about">About</a>
                <a class="nav-link" href="/tickets">Submit Ticket</a>
                <a class="nav-link" href="/contact">Contact</a>
                <a class="nav-link" href="/login">Staff Login</a>
            </div>
        </div>
    </nav>
    
    <div class="hero">
        <div class="container">
            <h1 class="display-4">Welcome to HelpDesk Pro</h1>
            <p class="lead">Your comprehensive support ticket management solution</p>
            <a href="/tickets/new" class="btn btn-light btn-lg mt-3">Submit a Ticket</a>
        </div>
    </div>
    
    <div class="container py-5">
        <div class="row">
            <div class="col-md-4 mb-4">
                <div class="card h-100 text-center p-4">
                    <div class="feature-icon">&#128221;</div>
                    <h5>Easy Submission</h5>
                    <p class="text-muted">Submit support tickets quickly and easily through our intuitive interface.</p>
                </div>
            </div>
            <div class="col-md-4 mb-4">
                <div class="card h-100 text-center p-4">
                    <div class="feature-icon">&#128269;</div>
                    <h5>Track Progress</h5>
                    <p class="text-muted">Monitor the status of your tickets in real-time.</p>
                </div>
            </div>
            <div class="col-md-4 mb-4">
                <div class="card h-100 text-center p-4">
                    <div class="feature-icon">&#128274;</div>
                    <h5>Secure Platform</h5>
                    <p class="text-muted">Your data is protected with enterprise-grade security.</p>
                </div>
            </div>
        </div>
    </div>
    
    <footer class="bg-dark text-white text-center py-3">
        <p class="mb-0">&copy; 2024 HelpDesk Pro v0.3.0. All rights reserved.</p>
    </footer>
</body>
</html>
"""

ABOUT_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>About - HelpDesk Pro</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <style>
        body { background: #f8f9fa; }
        .navbar { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .nav-link { color: rgba(255,255,255,0.8) !important; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/">HelpDesk Pro</a>
            <div class="navbar-nav ml-auto">
                <a class="nav-link" href="/about">About</a>
                <a class="nav-link" href="/tickets">Submit Ticket</a>
                <a class="nav-link" href="/contact">Contact</a>
                <a class="nav-link" href="/login">Staff Login</a>
            </div>
        </div>
    </nav>
    <div class="container py-5">
        <h1>About HelpDesk Pro</h1>
        <p class="lead">HelpDesk Pro is a comprehensive ticket management system designed for businesses of all sizes.</p>
        <h3>Features</h3>
        <ul>
            <li>Simple ticket submission for customers</li>
            <li>Powerful staff dashboard for ticket management</li>
            <li>Real-time status updates</li>
            <li>Priority-based routing</li>
        </ul>
        <p>Version: 0.3.0</p>
    </div>
</body>
</html>
"""

CONTACT_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Contact - HelpDesk Pro</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <style>
        body { background: #f8f9fa; }
        .navbar { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .nav-link { color: rgba(255,255,255,0.8) !important; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/">HelpDesk Pro</a>
            <div class="navbar-nav ml-auto">
                <a class="nav-link" href="/about">About</a>
                <a class="nav-link" href="/tickets">Submit Ticket</a>
                <a class="nav-link" href="/contact">Contact</a>
                <a class="nav-link" href="/login">Staff Login</a>
            </div>
        </div>
    </nav>
    <div class="container py-5">
        <h1>Contact Us</h1>
        <p>Email: support@helpdeskpro.example.com</p>
        <p>Phone: +1 (555) 123-4567</p>
        <p>Hours: Monday-Friday 9AM-5PM EST</p>
    </div>
</body>
</html>
"""

LOGIN_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Staff Login - HelpDesk Pro</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <style>
        body {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
        .login-card {{ max-width: 400px; margin: 100px auto; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="card login-card">
            <div class="card-header text-center">
                <h4>Staff Login</h4>
            </div>
            <div class="card-body">
                {error_msg}
                <form method="post">
                    <div class="form-group">
                        <label>Username</label>
                        <input type="text" name="username" class="form-control" placeholder="Enter username">
                    </div>
                    <div class="form-group">
                        <label>Password</label>
                        <input type="password" name="password" class="form-control" placeholder="Enter password">
                    </div>
                    <button type="submit" class="btn btn-primary btn-block">Login</button>
                </form>
                <hr>
                <p class="text-muted text-center mb-0">Staff portal for ticket management</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

TICKET_LIST_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Tickets - HelpDesk Pro</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <style>
        body { background: #f8f9fa; }
        .navbar { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .nav-link { color: rgba(255,255,255,0.8) !important; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/">HelpDesk Pro</a>
            <div class="navbar-nav ml-auto">
                <a class="nav-link" href="/about">About</a>
                <a class="nav-link" href="/tickets">Submit Ticket</a>
                <a class="nav-link" href="/contact">Contact</a>
                <a class="nav-link" href="/login">Staff Login</a>
            </div>
        </div>
    </nav>
    <div class="container py-5">
        <h1>Support Tickets</h1>
        <p class="lead">Browse open tickets or submit a new one</p>
        <a href="/tickets/new" class="btn btn-primary mb-3">Submit New Ticket</a>
        <div class="alert alert-info">
            <strong>Note:</strong> To view and manage all tickets, please <a href="/login">login as staff</a>.
        </div>
    </div>
</body>
</html>
"""

NEW_TICKET_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>New Ticket - HelpDesk Pro</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <style>
        body { background: #f8f9fa; }
        .navbar { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .nav-link { color: rgba(255,255,255,0.8) !important; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/">HelpDesk Pro</a>
            <div class="navbar-nav ml-auto">
                <a class="nav-link" href="/about">About</a>
                <a class="nav-link" href="/tickets">Submit Ticket</a>
                <a class="nav-link" href="/contact">Contact</a>
                <a class="nav-link" href="/login">Staff Login</a>
            </div>
        </div>
    </nav>
    <div class="container py-5">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">
                        <h4 class="mb-0">Submit New Support Ticket</h4>
                    </div>
                    <div class="card-body">
                        <form method="post">
                            <div class="form-group">
                                <label>Your Email</label>
                                <input type="email" name="email" class="form-control" placeholder="your@email.com">
                            </div>
                            <div class="form-group">
                                <label>Ticket Title *</label>
                                <input type="text" name="title" class="form-control" placeholder="Brief description of your issue" required>
                            </div>
                            <div class="form-group">
                                <label>Description</label>
                                <textarea name="description" class="form-control" rows="5" placeholder="Provide details about your issue..."></textarea>
                            </div>
                            <div class="form-group">
                                <label>Priority</label>
                                <select name="priority" class="form-control">
                                    <option value="Low">Low</option>
                                    <option value="Medium" selected>Medium</option>
                                    <option value="High">High</option>
                                </select>
                            </div>
                            <button type="submit" class="btn btn-primary">Submit Ticket</button>
                            <a href="/tickets" class="btn btn-secondary">Cancel</a>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

TICKET_VIEW_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Staff Dashboard - HelpDesk Pro</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <style>
        body {{ background: #f8f9fa; }}
        .navbar {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
        .nav-link {{ color: rgba(255,255,255,0.8) !important; }}
        .table th {{ background: #343a40; color: white; }}
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/">HelpDesk Pro</a>
            <div class="navbar-nav ml-auto">
                <a class="nav-link" href="/tickets/view">Dashboard</a>
                <a class="nav-link" href="/tickets/new">New Ticket</a>
                <a class="nav-link" href="/">Logout</a>
            </div>
        </div>
    </nav>
    <div class="container-fluid py-4">
        <!-- FLAG_PLACEHOLDER -->
        <h2>Ticket Dashboard</h2>
        <p class="text-muted">Viewing all support tickets</p>
        <div class="card">
            <div class="card-body">
                <table class="table table-striped table-hover">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Title</th>
                            <th>Status</th>
                            <th>Priority</th>
                            <th>Created</th>
                        </tr>
                    </thead>
                    <tbody>
                        {ticket_rows}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>
"""

TICKET_DETAIL_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Ticket #{id} - HelpDesk Pro</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <style>
        body {{ background: #f8f9fa; }}
        .navbar {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
        .nav-link {{ color: rgba(255,255,255,0.8) !important; }}
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/">HelpDesk Pro</a>
            <div class="navbar-nav ml-auto">
                <a class="nav-link" href="/tickets/view">Dashboard</a>
                <a class="nav-link" href="/tickets/new">New Ticket</a>
            </div>
        </div>
    </nav>
    <div class="container py-5">
        <div class="card">
            <div class="card-header">
                <h4>Ticket #{id}: {title}</h4>
            </div>
            <div class="card-body">
                <p><strong>Status:</strong> {status}</p>
                <p><strong>Priority:</strong> {priority}</p>
                <p><strong>Created By:</strong> {created_by}</p>
                <p><strong>Created At:</strong> {created_at}</p>
            </div>
        </div>
        <a href="/tickets/view" class="btn btn-secondary mt-3">Back to Dashboard</a>
    </div>
</body>
</html>
"""

# Legacy constants kept for compatibility (not used in new helpdesk implementation)
IMAGE_ROUTES = {
    "xss_easy": {
        "start": "static/img/cookies/new_circle.png",
        "process": "static/img/cookies/error_circle.png",
        "error": "static/img/cookies/error_circle.png",
        "success": "static/img/cookies/success_circle.png"
    }
}
