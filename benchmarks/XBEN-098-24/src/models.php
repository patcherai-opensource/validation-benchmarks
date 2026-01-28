<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Models - DeepVision</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="sidebar">
        <div class="logo">
        <img src="images/logo.png" width="120" height="100">
        </div>
        <ul>
            <li><a href="/index.php">Home</a></li>
            <li><a href="/docs.php">API Docs</a></li>
            <li><a href="/models.php">Models</a></li>
            <li><a href="/datasets.php">Datasets</a></li>
            <li><a href="/login.php">Login</a></li>
        </ul>
    </div>
    <div class="content">
        <h1>Pre-trained Models</h1>
        
        <h2>Available Models</h2>
        <table border="1" cellpadding="10">
            <tr><th>Model ID</th><th>Name</th><th>Type</th><th>Status</th></tr>
            <tr><td>resnet50-v2</td><td>ResNet-50 V2</td><td>Classification</td><td>Active</td></tr>
            <tr><td>yolov5-large</td><td>YOLOv5 Large</td><td>Object Detection</td><td>Active</td></tr>
            <tr><td>unet-seg</td><td>U-Net Segmentation</td><td>Segmentation</td><td>Active</td></tr>
            <tr><td>efficientnet-b7</td><td>EfficientNet B7</td><td>Classification</td><td>Active</td></tr>
            <tr><td>detr-panoptic</td><td>DETR Panoptic</td><td>Detection</td><td>Beta</td></tr>
        </table>
        
        <h2>Model Usage</h2>
        <pre>
# Python SDK Example
from deepvision import Client

client = Client(api_key="your-api-key")
result = client.predict(
    model_id="resnet50-v2",
    image_path="./sample.jpg"
)
print(result.labels)
        </pre>
        
        <h2>Custom Models</h2>
        <p>Enterprise customers can upload custom trained models. Contact sales@deepvision.local for more information.</p>
    </div>
</body>
</html>
