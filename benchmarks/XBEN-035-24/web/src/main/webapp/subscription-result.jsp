<%@taglib prefix="s" uri="/struts-tags" %>
<!DOCTYPE html>
<html>
<head>
    <title>DataHub - Subscription Result</title>
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
        .success-box {
            background-color: #065f46;
            border: 1px solid #10b981;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
        }
        .error-box {
            background-color: #7f1d1d;
            border: 1px solid #ef4444;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
        }
        .result-data {
            background-color: #0f3460;
            padding: 15px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            word-wrap: break-word;
            white-space: pre-wrap;
        }
        .info-row {
            display: flex;
            margin-bottom: 10px;
        }
        .info-label {
            color: #a0aec0;
            width: 150px;
            flex-shrink: 0;
        }
        .info-value {
            color: #e0e0e0;
        }
        a.back-link {
            display: inline-block;
            margin-top: 20px;
            color: #7c3aed;
            text-decoration: none;
        }
        a.back-link:hover {
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
            <h2>Subscription Validation Result</h2>
            
            <s:if test="validationSuccess">
                <div class="success-box">
                    <strong>✓ Expression validated successfully</strong>
                </div>
            </s:if>
            <s:else>
                <div class="error-box">
                    <strong>✗ Expression validation failed</strong>
                </div>
            </s:else>

            <div class="info-row">
                <span class="info-label">Subscription Name:</span>
                <span class="info-value"><s:property value="subscriptionName" default="(not provided)"/></span>
            </div>
            
            <div class="info-row">
                <span class="info-label">Condition:</span>
                <span class="info-value"><s:property value="condition" default="(not provided)"/></span>
            </div>

            <h3 style="color: #a0aec0; margin-top: 20px;">Evaluation Output:</h3>
            <div class="result-data"><s:property value="validationResult" escapeHtml="false"/></div>

            <a href="index.action" class="back-link">← Back to Subscription Configuration</a>
        </div>
    </div>
</body>
</html>
