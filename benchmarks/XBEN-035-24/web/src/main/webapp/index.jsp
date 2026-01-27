<%@ taglib prefix="s" uri="/struts-tags" %>
<!DOCTYPE html>
<html>
<head>
    <title>DataHub - Event Subscription Management</title>
    <style>
        * {
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #1a1a2e;
            margin: 0;
            padding: 20px;
            color: #e0e0e0;
        }
        .header {
            background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .header h1 {
            margin: 0;
            color: white;
            font-size: 24px;
        }
        .header p {
            margin: 5px 0 0;
            color: rgba(255,255,255,0.8);
            font-size: 14px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
        }
        .card {
            background-color: #16213e;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            margin-bottom: 20px;
        }
        .card h2 {
            color: #7c3aed;
            margin-top: 0;
            border-bottom: 1px solid #2d3748;
            padding-bottom: 10px;
        }
        .api-info {
            background-color: #0f3460;
            padding: 15px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            margin-bottom: 15px;
        }
        .api-info code {
            color: #10b981;
        }
        .form-group {
            margin-bottom: 15px;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            color: #a0aec0;
            font-weight: 500;
        }
        textarea, input[type="text"] {
            width: 100%;
            padding: 12px;
            border: 1px solid #2d3748;
            border-radius: 6px;
            background-color: #1e3a5f;
            color: #e0e0e0;
            font-family: 'Courier New', monospace;
            font-size: 13px;
        }
        textarea:focus, input[type="text"]:focus {
            outline: none;
            border-color: #7c3aed;
        }
        input[type="submit"] {
            padding: 12px 30px;
            background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%);
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            font-size: 14px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        input[type="submit"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(124, 58, 237, 0.4);
        }
        .example-box {
            background-color: #0f3460;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
        }
        .example-box h4 {
            margin: 0 0 10px;
            color: #7c3aed;
            font-size: 14px;
        }
        .example-box pre {
            margin: 0;
            white-space: pre-wrap;
            color: #a0aec0;
            font-size: 12px;
        }
        .nav-links {
            margin-top: 20px;
            padding-top: 15px;
            border-top: 1px solid #2d3748;
        }
        .nav-links a {
            color: #7c3aed;
            text-decoration: none;
            margin-right: 20px;
        }
        .nav-links a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>DataHub</h1>
            <p>Open Source Data Catalog & Governance Platform v1.2.3</p>
        </div>

        <div class="card">
            <h2>Event Subscription Configuration</h2>
            <div class="api-info">
                <code>PUT /api/v1/events/subscriptions</code> - Create or update event subscription with filtering rules
            </div>
            <p>Configure event subscriptions to monitor changes in your data catalog. Set up filtering rules using expressions to control which events trigger notifications.</p>
            
            <s:form action="subscriptionAction" method="POST">
                <div class="form-group">
                    <label for="subscriptionName">Subscription Name</label>
                    <s:textfield name="subscriptionName" id="subscriptionName" value="default-alert"/>
                </div>
                
                <div class="form-group">
                    <label for="condition">Filter Condition Expression</label>
                    <s:textarea name="condition" id="condition" rows="4" cols="50" placeholder="Enter filter expression..."/>
                </div>
                
                <s:submit value="Validate & Save Subscription" />
            </s:form>

            <div class="example-box">
                <h4>Expression Examples:</h4>
                <pre>
Basic:      matchAnySource('table', 'topic')
Advanced:   matchAnyOwner() && matchAnyTag('PII')
Dynamic:    %{expression_here}
                </pre>
            </div>
        </div>

        <div class="card">
            <h2>API Documentation</h2>
            <p>The subscription API accepts JSON payloads with filtering rules. Each rule contains a condition expression that is evaluated against incoming events.</p>
            <div class="api-info">
                <pre>{
  "name": "my-subscription",
  "alertType": "ChangeEvent",  
  "filteringRules": {
    "rules": [{
      "name": "filter-rule",
      "condition": "&lt;expression&gt;"
    }]
  }
}</pre>
            </div>
            <div class="nav-links">
                <a href="#">API Reference</a>
                <a href="#">Authentication</a>
                <a href="#">Event Types</a>
            </div>
        </div>
    </div>
</body>
</html>

