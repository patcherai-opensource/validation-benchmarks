<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AppBuilder Admin Portal</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <h1>AppBuilder REST API</h1>
    <p>Version 3.3.0</p>
    
    <div class="api-info">
        <h2>API Documentation</h2>
        <p>This application provides a REST API for managing resources. Authentication is required for most endpoints.</p>
        
        <h3>Available Endpoints</h3>
        <table class="endpoints-table">
            <tr>
                <th>Method</th>
                <th>Endpoint</th>
                <th>Description</th>
            </tr>
            <tr>
                <td>POST</td>
                <td><code>/api/v1/security/login</code></td>
                <td>Authenticate and obtain access token</td>
            </tr>
            <tr>
                <td>GET</td>
                <td><code>/api/v1/users/</code></td>
                <td>List users (requires authentication)</td>
            </tr>
            <tr>
                <td>GET</td>
                <td><code>/api/v1/roles/</code></td>
                <td>List roles (requires authentication)</td>
            </tr>
        </table>
        
        <h3>Authentication</h3>
        <p>To authenticate, send a POST request to <code>/api/v1/security/login</code> with JSON body:</p>
        <pre>
{
    "username": "your_username",
    "password": "your_password",
    "provider": "db"
}
        </pre>
        
        <p>Supported authentication providers:</p>
        <ul>
            <li><code>db</code> - Database authentication (default)</li>
            <li><code>ldap</code> - LDAP/Active Directory authentication</li>
        </ul>
        
        <h3>Response</h3>
        <p>On successful authentication, you will receive an access token and user information.</p>
    </div>
    
    <div class="footer">
        <p>Powered by Flask-AppBuilder | <a href="/swagger/v1">Swagger UI</a></p>
    </div>
</div>
</body>
</html>
