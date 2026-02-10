<?php
class RstParser {
    private $environment;
    
    public function __construct($basePath = '') {
        $this->environment = new RstEnvironment($basePath);
    }
    
    public function parse($document) {
        $document = $this->includeFiles($document);
        $html = $this->parseDocument($document);
        return $html;
    }
    
    public function includeFiles($document) {
        $parser = $this;
        $environment = $this->environment;
        
        return preg_replace_callback('/^\.\. include:: (.+)$/m', function($match) use ($parser, $environment) {
            $path = $environment->absoluteRelativePath(trim($match[1]));
            if (file_exists($path)) {
                return $parser->includeFiles(file_get_contents($path));
            }
            return '';
        }, $document);
    }
    
    private function parseDocument($document) {
        $lines = explode("\n", $document);
        $html = '';
        $inCodeBlock = false;
        $codeContent = '';
        $inBlockquote = false;
        $blockquoteContent = '';
        
        for ($i = 0; $i < count($lines); $i++) {
            $line = $lines[$i];
            $nextLine = isset($lines[$i + 1]) ? $lines[$i + 1] : '';
            
            if (preg_match('/^\.\. code-block::/i', $line)) {
                $inCodeBlock = true;
                continue;
            }
            
            if ($inCodeBlock) {
                if (preg_match('/^\s{3,}/', $line) || trim($line) === '') {
                    $codeContent .= htmlspecialchars(preg_replace('/^\s{3}/', '', $line)) . "\n";
                } else {
                    $html .= '<pre><code>' . trim($codeContent) . '</code></pre>';
                    $codeContent = '';
                    $inCodeBlock = false;
                }
            }
            
            if (preg_match('/^={3,}$/', $nextLine) && trim($line) !== '') {
                $html .= '<h1>' . htmlspecialchars(trim($line)) . '</h1>';
                $i++;
                continue;
            }
            
            if (preg_match('/^-{3,}$/', $nextLine) && trim($line) !== '') {
                $html .= '<h2>' . htmlspecialchars(trim($line)) . '</h2>';
                $i++;
                continue;
            }
            
            if (preg_match('/^~{3,}$/', $nextLine) && trim($line) !== '') {
                $html .= '<h3>' . htmlspecialchars(trim($line)) . '</h3>';
                $i++;
                continue;
            }
            
            if (preg_match('/^\*\*(.+)\*\*$/', trim($line), $matches)) {
                $html .= '<p><strong>' . htmlspecialchars($matches[1]) . '</strong></p>';
                continue;
            }
            
            if (preg_match('/^\*(.+)\*$/', trim($line), $matches)) {
                $html .= '<p><em>' . htmlspecialchars($matches[1]) . '</em></p>';
                continue;
            }
            
            if (preg_match('/^- (.+)$/', $line, $matches)) {
                $html .= '<li>' . htmlspecialchars($matches[1]) . '</li>';
                continue;
            }
            
            if (preg_match('/^\d+\. (.+)$/', $line, $matches)) {
                $html .= '<li>' . htmlspecialchars($matches[1]) . '</li>';
                continue;
            }
            
            if (!$inCodeBlock && trim($line) !== '' && !preg_match('/^\.\. /', $line)) {
                $html .= '<p>' . htmlspecialchars(trim($line)) . '</p>';
            }
        }
        
        if ($inCodeBlock && $codeContent !== '') {
            $html .= '<pre><code>' . trim($codeContent) . '</code></pre>';
        }
        
        return $html;
    }
}

class RstEnvironment {
    private $basePath;
    
    public function __construct($basePath = '') {
        $this->basePath = $basePath;
    }
    
    public function absoluteRelativePath($path) {
        if ($this->basePath !== '') {
            return $this->basePath . '/' . $path;
        }
        return $path;
    }
}

$preview_content = '';
$rst_input = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['rst_content'])) {
    $rst_input = $_POST['rst_content'];
    $parser = new RstParser();
    $preview_content = $parser->parse($rst_input);
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF8">
    <title>Encoder64 Blog | Documentation Preview</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .preview-area {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 20px;
            min-height: 200px;
        }
        .preview-area pre {
            background-color: #272822;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 4px;
        }
        .rst-textarea {
            font-family: monospace;
            min-height: 300px;
        }
    </style>
</head>
<body>
    <? include("include/navigation-bar.php") ?>

    <header class="py-5 bg-light border-bottom mb-4">
        <div class="container">
            <div class="text-center my-5">
                <h1 class="fw-bolder">Documentation Preview</h1>
                <p class="lead mb-0">Preview your reStructuredText documentation before submission</p>
            </div>
        </div>
    </header>

    <div class="container">
        <div class="row">
            <div class="col-md-8">
                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">RST Editor</h5>
                    </div>
                    <div class="card-body">
                        <form method="POST" action="">
                            <div class="mb-3">
                                <label for="rst_content" class="form-label">Enter your reStructuredText content:</label>
                                <textarea name="rst_content" id="rst_content" class="form-control rst-textarea" placeholder="Enter RST content here..."><?php echo htmlspecialchars($rst_input); ?></textarea>
                            </div>
                            <button type="submit" class="btn btn-primary">Preview</button>
                        </form>
                    </div>
                </div>

                <?php if ($preview_content !== ''): ?>
                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">Preview</h5>
                    </div>
                    <div class="card-body preview-area">
                        <?php echo $preview_content; ?>
                    </div>
                </div>
                <?php endif; ?>

                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">RST Quick Reference</h5>
                    </div>
                    <div class="card-body">
                        <h6>Headers</h6>
                        <pre>Title
=====

Subtitle
--------

Section
~~~~~~~</pre>
                        
                        <h6 class="mt-3">Lists</h6>
                        <pre>- Item 1
- Item 2

1. First
2. Second</pre>
                        
                        <h6 class="mt-3">Emphasis</h6>
                        <pre>*italic*
**bold**</pre>
                        
                        <h6 class="mt-3">Code Blocks</h6>
                        <pre>.. code-block:: python

   def hello():
       print("Hello, World!")</pre>
                    </div>
                </div>
            </div>
            <? include("include/sidebar.php") ?>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
