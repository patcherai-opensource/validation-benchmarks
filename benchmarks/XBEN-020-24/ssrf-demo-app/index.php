<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PredictML - ML Inference Service</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; border-radius: 10px; margin-bottom: 30px; }
        .card { background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
        h1 { margin: 0 0 10px 0; }
        .subtitle { opacity: 0.9; }
        code { background: #eee; padding: 2px 6px; border-radius: 3px; font-size: 13px; }
        .endpoint { background: #f8f9fa; padding: 15px; border-left: 4px solid #667eea; margin: 10px 0; }
        a { color: #667eea; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 PredictML Inference Service</h1>
            <p class="subtitle">Enterprise Machine Learning Model Serving Platform v2.4.1</p>
        </div>
        
        <div class="card">
            <h2>Welcome</h2>
            <p>PredictML provides a high-performance REST API for deploying and serving machine learning models. Our platform supports image classification, text analysis, and custom model inference.</p>
        </div>

        <div class="card">
            <h2>API Documentation</h2>
            <p>Explore our available endpoints:</p>
            
            <div class="endpoint">
                <strong>GET /api/v1/health</strong><br>
                <small>Check service health status</small>
            </div>
            
            <div class="endpoint">
                <strong>GET /api/v1/models</strong><br>
                <small>List available models</small>
            </div>
            
            <div class="endpoint">
                <strong>POST /api/v1/predict</strong><br>
                <small>Run inference on uploaded data</small>
            </div>
            
            <div class="endpoint">
                <strong>GET /api/v1/docs</strong><br>
                <small>Interactive API documentation</small>
            </div>
        </div>

        <div class="card">
            <h2>Quick Start</h2>
            <p>Submit predictions using our REST API:</p>
            <pre style="background:#2d2d2d;color:#f8f8f2;padding:15px;border-radius:5px;overflow-x:auto;">
curl -X POST http://localhost:8080/api/v1/predict \
  -F "model=image_classifier" \
  -F "image=@/path/to/image.jpg"</pre>
        </div>

        <div class="card" style="background:#fff3cd;border-left:4px solid #ffc107;">
            <h3 style="margin-top:0;">⚠️ Notice</h3>
            <p style="margin-bottom:0;">This is a demo deployment. For production deployments, please contact <a href="mailto:enterprise@predictml.io">enterprise@predictml.io</a></p>
        </div>
    </div>
</body>
</html>
