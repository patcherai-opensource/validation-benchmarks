<?php
    include 'config.php';
?>
<!doctype html>
<html>
    <head>
        <title>NoteHub CRM - API Documentation</title>
        <link rel="stylesheet" href="static/styles.css">
        <link rel="icon" href="static/favicon.ico" type="image/x-icon">
    </head>
    <body>
        &nbsp;</br>
        <div class="center blue">
            <div class="logo">NoteHub CRM</div>
            <h1>API Documentation</h1>
            <h3>REST API Endpoints</h3>
            <table width="100%" border="1" cellpadding="5">
                <tr>
                    <th>Method</th>
                    <th>Endpoint</th>
                    <th>Description</th>
                </tr>
                <tr>
                    <td>POST</td>
                    <td>/api/auth</td>
                    <td>Authenticate user and get session token</td>
                </tr>
                <tr>
                    <td>GET</td>
                    <td>/api/notes</td>
                    <td>List all notes for authenticated user</td>
                </tr>
                <tr>
                    <td>POST</td>
                    <td>/api/notes</td>
                    <td>Create a new note</td>
                </tr>
                <tr>
                    <td>GET</td>
                    <td>/api/profile</td>
                    <td>Get current user profile</td>
                </tr>
            </table>
            <br>
            <h3>Internal Maintenance API</h3>
            <p><em>For upgrade wizard and system administration only.</em></p>
            <p>The maintenance API is accessed during system upgrades. These endpoints require proper authorization.</p>
            <br>
            <a class="button" href="sign-in.php">Back to Login</a>
        </div>
        <div class="footer">
            <p>&copy; 2024 NoteHub CRM | <a href="about.php">About</a> | <a href="api-docs.php">API</a></p>
        </div>
    </body>
</html>
