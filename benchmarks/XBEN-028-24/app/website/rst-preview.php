<?php
/**
 * RST Document Preview
 * 
 * This endpoint allows users to preview reStructuredText documents
 * before submitting them for publication.
 */

require_once 'rst/RstParser.php';

$result = '';
$error = '';
$rst_content = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['rst_content']) && !empty(trim($_POST['rst_content']))) {
        $rst_content = $_POST['rst_content'];
        
        try {
            $parser = new RstParser('/var/www/html/docs');
            $result = $parser->parse($rst_content);
        } catch (Exception $e) {
            $error = "Error parsing RST: " . htmlspecialchars($e->getMessage());
        }
    } else {
        $error = "Please provide RST content to preview.";
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Encoder64 Blog | RST Preview</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .preview-box {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            padding: 20px;
            border-radius: 5px;
            min-height: 200px;
        }
        .rst-editor {
            font-family: monospace;
            min-height: 300px;
        }
    </style>
</head>
<body>
    <!-- Navigation Bar -->
    <? include("include/navigation-bar.php") ?>

    <!-- Header -->
    <header class="py-5 bg-light border-bottom mb-4">
        <div class="container">
            <div class="text-center my-5">
                <h1 class="fw-bolder">RST Document Preview</h1>
                <p class="lead">Preview your reStructuredText documents before submission</p>
            </div>
        </div>
    </header>

    <!-- Main Content Section -->
    <div class="container">
        <div class="row">
            <div class="col-md-8">
                <div class="container mt-3">
                    <h3>RST Editor</h3>
                    <p>Enter your reStructuredText content below to see a live preview. Our parser supports common RST directives including:</p>
                    <ul>
                        <li>Headers (using = or - underlines)</li>
                        <li>Bold text (**text**)</li>
                        <li>Italic text (*text*)</li>
                        <li>Code blocks (.. code-block::)</li>
                        <li>File includes (.. include:: path/to/file)</li>
                    </ul>
                    
                    <form method="post" action="">
                        <div class="mb-3">
                            <label for="rst_content" class="form-label">RST Content</label>
                            <textarea class="form-control rst-editor" id="rst_content" name="rst_content" rows="12" placeholder="Enter your reStructuredText here..."><?= htmlspecialchars($rst_content); ?></textarea>
                        </div>
                        <button type="submit" class="btn btn-primary">Preview</button>
                    </form>
                    
                    <?php if ($error): ?>
                        <div class="alert alert-danger mt-4"><?= $error; ?></div>
                    <?php endif; ?>
                    
                    <?php if ($result): ?>
                        <hr class="my-4">
                        <h3>Preview Output</h3>
                        <div class="preview-box">
                            <?= $result; ?>
                        </div>
                    <?php endif; ?>
                    
                    <hr class="my-4">
                    <h4>Example RST Document</h4>
                    <pre class="bg-light p-3">
Welcome to Encoder64
====================

This is an *example* RST document with **bold text**.

Features
--------

* Item one
* Item two

You can include inline code like ``print("Hello")``.

Visit `our website <https://example.com>`_ for more info.
                    </pre>
                </div>
            </div>
            
            <!-- Sidebar Widgets Column -->
            <? include("include/sidebar.php") ?>
        </div>
    </div>

    <!-- Bootstrap core JavaScript -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
