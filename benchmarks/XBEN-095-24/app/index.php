<?php session_start();?> 

<!DOCTYPE html>
<html>
<head>
    <title>Pimcore CMF - Customer Management Framework</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
        h3 { color: #555; }
        .nav-section { margin: 20px 0; }
        .nav-link { display: block; padding: 10px 15px; background: #f8f9fa; margin: 5px 0; text-decoration: none; color: #007bff; border-radius: 4px; }
        .nav-link:hover { background: #e9ecef; }
        .admin-section { background: #fff3cd; padding: 15px; border-radius: 4px; border-left: 4px solid #ffc107; margin-top: 20px; }
        .api-info { background: #e7f3ff; padding: 15px; border-radius: 4px; margin-top: 20px; }
        code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 Pimcore Customer Management Framework</h1>
        <p>Welcome to the Customer Management Framework admin interface.</p>
        
        <div class="nav-section">
            <h3>📋 Content Management</h3>
            <a class="nav-link" href="/segment-assignment.php?action=list-elements&type=object">View Objects</a>
            <a class="nav-link" href="/segment-assignment.php?action=list-elements&type=document">View Documents</a>
            <a class="nav-link" href="/segment-assignment.php?action=list-elements&type=asset">View Assets</a>
            <a class="nav-link" href="/segment-assignment.php?action=list-segments">View Segments</a>
        </div>
        
        <div class="admin-section">
            <h3>⚙️ Admin Functions</h3>
            <p>Segment Assignment Controller - Manage inheritable segments for objects, documents, and assets.</p>
            <a class="nav-link" href="/segment-assignment.php?action=inheritable-segments&id=1&type=object">Get Inheritable Segments (Object #1)</a>
            <a class="nav-link" href="/segment-assignment.php?action=inheritable-segments&id=1&type=document">Get Inheritable Segments (Document #1)</a>
        </div>
        
        <div class="api-info">
            <h3>📡 API Endpoint</h3>
            <p><strong>Endpoint:</strong> <code>/segment-assignment.php</code></p>
            <p><strong>Parameters:</strong></p>
            <ul>
                <li><code>action</code> - The action to perform (inheritable-segments, list-segments, list-elements)</li>
                <li><code>id</code> - Element ID (required for inheritable-segments)</li>
                <li><code>type</code> - Element type: object, document, or asset</li>
            </ul>
            <p><strong>Example:</strong> <code>/segment-assignment.php?action=inheritable-segments&id=1&type=object</code></p>
        </div>
    </div>
</body>
</html>
