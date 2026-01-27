<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PIM Media Manager - Product Image Upload</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            max-width: 600px;
            width: 100%;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #333;
            font-size: 24px;
            margin-bottom: 8px;
        }
        .header p {
            color: #666;
            font-size: 14px;
        }
        .logo {
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 16px;
            margin: 0 auto 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 32px;
            font-weight: bold;
        }
        .upload-form {
            border: 2px dashed #ddd;
            border-radius: 12px;
            padding: 30px;
            text-align: center;
            margin-bottom: 20px;
            transition: border-color 0.3s;
        }
        .upload-form:hover { border-color: #667eea; }
        .upload-form input[type="file"] {
            display: block;
            margin: 15px auto;
            padding: 10px;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }
        .message {
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            text-align: center;
        }
        .success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .info {
            background: #e7f3ff;
            color: #0c5460;
            border: 1px solid #b8daff;
            font-size: 13px;
            margin-top: 20px;
        }
        .file-link {
            word-break: break-all;
            font-family: monospace;
            background: #f8f9fa;
            padding: 8px;
            border-radius: 4px;
            display: block;
            margin-top: 10px;
        }
        .recent-uploads {
            margin-top: 30px;
            border-top: 1px solid #eee;
            padding-top: 20px;
        }
        .recent-uploads h3 {
            color: #333;
            font-size: 16px;
            margin-bottom: 15px;
        }
        .upload-item {
            display: flex;
            align-items: center;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 8px;
            margin-bottom: 8px;
        }
        .upload-item img {
            width: 40px;
            height: 40px;
            object-fit: cover;
            border-radius: 4px;
            margin-right: 12px;
        }
        .upload-item span {
            color: #666;
            font-size: 13px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">PIM</div>
            <h1>Product Image Manager</h1>
            <p>Upload product media assets for your catalog</p>
        </div>

        <form class="upload-form" method="POST" enctype="multipart/form-data" action="upload.php">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#667eea" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="17,8 12,3 7,8"></polyline>
                <line x1="12" y1="3" x2="12" y2="15"></line>
            </svg>
            <p style="margin-top: 15px; color: #666;">Drag and drop your product image here</p>
            <p style="color: #999; font-size: 12px; margin-top: 5px;">or click to browse</p>
            <input type="file" name="product_image" />
            <button type="submit" class="btn">Upload Image</button>
        </form>

        <div class="info">
            <strong>Supported formats:</strong> JPG, PNG, GIF, WebP<br>
            <strong>Max file size:</strong> 10MB<br>
            <!-- Media files are processed by Apache mod_php for thumbnail generation -->
            <!-- Configuration: FilesMatch \.php$ SetHandler application/x-httpd-php -->
        </div>

        <div class="recent-uploads">
            <h3>Recent Uploads</h3>
            <div class="upload-item">
                <img src="./static/sample_product.jpg" alt="Sample">
                <span>sample_product.jpg - 2.3 MB</span>
            </div>
            <div class="upload-item">
                <img src="./static/catalog_item.jpg" alt="Catalog">
                <span>catalog_item.jpg - 1.8 MB</span>
            </div>
        </div>
    </div>
</body>
</html>

