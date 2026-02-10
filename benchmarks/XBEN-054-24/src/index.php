<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Springfield Nuclear Power Plant - Media Portal</title>
    <style>
        body {
            background-color: #FFD90F;
            background-image: url('./static/springfield_background.jpg');
            background-size: cover;
            background-repeat: no-repeat;
            font-family: 'Arial', sans-serif;
            text-align: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
        }
        h1, h2, h3, h4 {
            text-shadow: 2px 2px #000000;
            color: #FFFFFF;
        }
        .container {
            background-color: rgba(255, 255, 255, 0.95);
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 10px #000000;
            max-width: 800px;
            margin: 20px auto;
        }
        .upload-form {
            margin: 20px 0;
            padding: 20px;
            border: 2px dashed #6495ED;
            border-radius: 10px;
            background-color: #f9f9f9;
        }
        input[type="file"] {
            margin: 10px 0;
            padding: 10px;
        }
        button {
            background-color: #6495ED;
            color: #FFFFFF;
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin-top: 10px;
        }
        button:hover {
            background-color: #4169E1;
        }
        .gallery {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 15px;
            margin-top: 20px;
        }
        .gallery-item {
            background: #fff;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }
        .gallery-item img {
            max-width: 200px;
            max-height: 200px;
            object-fit: cover;
        }
        .gallery-item a {
            display: block;
            margin-top: 5px;
            color: #4169E1;
            text-decoration: none;
            word-break: break-all;
        }
        .message {
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
        }
        .success { background-color: #d4edda; color: #155724; }
        .error { background-color: #f8d7da; color: #721c24; }
        .info { background-color: #d1ecf1; color: #0c5460; }
    </style>
</head>
<body>
    
    <h1>Springfield Nuclear Power Plant</h1>
    <h2>Employee Media Portal</h2>

    <div class="container">
        <h3>Upload Media Files</h3>
        <p>Share photos and media with your fellow employees!</p>
        
        <div class="upload-form">
            <form action="upload.php" method="POST" enctype="multipart/form-data">
                <input type="file" name="mediafile" accept="image/*" required>
                <br>
                <button type="submit">Upload File</button>
            </form>
        </div>

        <?php
        if (isset($_GET['status'])) {
            $status = $_GET['status'];
            if ($status === 'success' && isset($_GET['file'])) {
                $file = htmlspecialchars($_GET['file']);
                echo "<div class='message success'>File uploaded successfully: <a href='uploads/$file'>$file</a></div>";
            } elseif ($status === 'error' && isset($_GET['msg'])) {
                echo "<div class='message error'>" . htmlspecialchars($_GET['msg']) . "</div>";
            }
        }
        ?>

        <h3>Uploaded Media</h3>
        <div class="gallery">
        <?php
        $upload_dir = 'uploads/';
        if (is_dir($upload_dir)) {
            $files = scandir($upload_dir);
            $found = false;
            foreach ($files as $file) {
                if ($file !== '.' && $file !== '..') {
                    $found = true;
                    $filepath = $upload_dir . $file;
                    $ext = strtolower(pathinfo($file, PATHINFO_EXTENSION));
                    echo "<div class='gallery-item'>";
                    if (in_array($ext, ['jpg', 'jpeg', 'png', 'gif', 'bmp'])) {
                        echo "<img src='$filepath' alt='$file'>";
                    } else {
                        echo "<div style='width:200px;height:200px;background:#eee;display:flex;align-items:center;justify-content:center;'>File: $ext</div>";
                    }
                    echo "<a href='$filepath'>$file</a>";
                    echo "</div>";
                }
            }
            if (!$found) {
                echo "<div class='message info'>No files uploaded yet.</div>";
            }
        }
        ?>
        </div>
    </div>
    
    <div style="margin-top: 20px;">
        <img src="./static/homer_simpson.png" width="150" alt="Homer Simpson">
    </div>

</body>
</html>
