<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Datasets - DeepVision</title>
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
        <h1>Dataset Management</h1>
        
        <h2>Public Datasets</h2>
        <table border="1" cellpadding="10">
            <tr><th>Dataset ID</th><th>Name</th><th>Size</th><th>Images</th></tr>
            <tr><td>imagenet-mini</td><td>ImageNet Mini</td><td>2.3 GB</td><td>50,000</td></tr>
            <tr><td>coco-2017</td><td>COCO 2017</td><td>18 GB</td><td>118,287</td></tr>
            <tr><td>cifar-100</td><td>CIFAR-100</td><td>161 MB</td><td>60,000</td></tr>
            <tr><td>pascal-voc</td><td>Pascal VOC 2012</td><td>2 GB</td><td>17,125</td></tr>
        </table>
        
        <h2>Upload Dataset</h2>
        <p>Upload your own datasets for custom model training:</p>
        <pre>
# CLI Upload
deepvision datasets upload \
    --name "my-dataset" \
    --path ./images/ \
    --format "imagefolder"
        </pre>
        
        <h2>Storage Quotas</h2>
        <ul>
            <li>Free tier: 5 GB</li>
            <li>Pro tier: 100 GB</li>
            <li>Enterprise: Unlimited</li>
        </ul>
    </div>
</body>
</html>
