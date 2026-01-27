<%@taglib prefix="s" uri="/struts-tags" %>
<!DOCTYPE html>
<html>
<head>
    <title>DataHub - API Response</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #1a1a2e;
            margin: 0;
            padding: 20px;
            color: #e0e0e0;
        }
        .container {
            max-width: 600px;
            margin: 50px auto;
            background-color: #16213e;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }
        h1 {
            color: #7c3aed;
            text-align: center;
        }
        .response-box {
            background-color: #0f3460;
            padding: 15px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>API Response</h1>
        <div class="response-box">
            <pre>{"status": "success", "message": "Request processed"}</pre>
        </div>
    </div>
</body>
</html>

