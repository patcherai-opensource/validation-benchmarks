<?php
$flag = "@FLAG@";

/**
 * XSS Detection Function
 * Checks if the input contains valid XSS payload patterns that would execute in a browser
 */
function detectXSSPayload($input) {
    // Must contain script execution vectors
    $xss_patterns = [
        // Script tags
        '/<script[^>]*>.*?<\/script>/is',
        '/<script[^>]*>/i',
        // Event handlers with JavaScript
        '/\bon\w+\s*=\s*["\']?[^"\']*(?:alert|confirm|prompt|eval|document|window|location|cookie|fetch|XMLHttpRequest)/i',
        '/\bon(?:error|load|click|mouseover|focus|blur|submit|change|input|keydown|keyup|keypress)\s*=/i',
        // JavaScript protocol
        '/javascript\s*:/i',
        // SVG with script
        '/<svg[^>]*\s+on\w+\s*=/i',
        // Img tag with onerror
        '/<img[^>]+onerror\s*=/i',
        // Body tag with onload
        '/<body[^>]+onload\s*=/i',
        // Iframe with javascript
        '/<iframe[^>]+src\s*=\s*["\']?javascript:/i',
    ];
    
    foreach ($xss_patterns as $pattern) {
        if (preg_match($pattern, $input)) {
            return true;
        }
    }
    return false;
}

?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DocuShare - Document Management System</title>
    <style>
        body {
            background-color: #1a1a2e;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #eaeaea;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: #16213e;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        h1 {
            color: #e94560;
            border-bottom: 2px solid #e94560;
            padding-bottom: 15px;
        }
        .nav {
            background: #0f3460;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .nav a {
            color: #eaeaea;
            text-decoration: none;
            margin-right: 20px;
            padding: 8px 15px;
            border-radius: 3px;
            transition: background 0.3s;
        }
        .nav a:hover {
            background: #e94560;
        }
        .documents {
            margin-top: 20px;
        }
        .document-item {
            background: #0f3460;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
        }
        .btn-danger {
            background: #e94560;
            color: white;
        }
        .btn-danger:hover {
            background: #ff6b6b;
        }
        .error-box {
            background: #2d1f1f;
            border: 1px solid #e94560;
            padding: 20px;
            border-radius: 5px;
            margin-top: 20px;
        }
        .error-box h3 {
            color: #e94560;
            margin-top: 0;
        }
        .success-box {
            background: #1f2d1f;
            border: 1px solid #4ade80;
            padding: 20px;
            border-radius: 5px;
            margin-top: 20px;
        }
        .footer {
            margin-top: 30px;
            text-align: center;
            color: #666;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📁 DocuShare v2.4.1</h1>
        <p>Enterprise Document Management System</p>
        
        <div class="nav">
            <a href="/">🏠 Home</a>
            <a href="/?page=documents">📄 Documents</a>
            <a href="/?page=attachments">📎 Attachments</a>
            <a href="/?action=delattachment">🗑️ Delete Attachment</a>
        </div>
        
        
        <?php
        // Handle delete attachment action - VULNERABLE TO XSS
        if (isset($_GET['action']) && $_GET['action'] === 'delattachment') {
            $filename = isset($_GET['filename']) ? $_GET['filename'] : '';
            
            if (empty($filename)) {
                echo '<div class="documents">';
                echo '<h2>Delete Attachment</h2>';
                echo '<p>Enter the attachment name to delete:</p>';
                echo '<form method="GET" action="">';
                echo '<input type="hidden" name="action" value="delattachment">';
                echo '<input type="text" name="filename" placeholder="attachment_name.pdf" style="padding: 10px; width: 300px; border-radius: 4px; border: 1px solid #444; background: #0f3460; color: #eaeaea;">';
                echo '<button type="submit" class="btn btn-danger" style="margin-left: 10px;">Delete</button>';
                echo '</form>';
                echo '</div>';
            } else {
                // List of valid attachments
                $valid_attachments = ['report_2024.pdf', 'budget.xlsx', 'meeting_notes.docx', 'presentation.pptx'];
                
                if (in_array($filename, $valid_attachments)) {
                    echo '<div class="success-box">';
                    echo '<h3>✓ Attachment Deleted Successfully</h3>';
                    echo '<p>The attachment <strong>' . htmlspecialchars($filename) . '</strong> has been removed.</p>';
                    echo '</div>';
                } else {
                    // VULNERABILITY: Filename is NOT escaped in error message (Reflected XSS)
                    // Check if the payload contains XSS - if so, reveal the flag
                    $xss_detected = detectXSSPayload($filename);
                    
                    echo '<div class="error-box">';
                    echo '<h3>⚠️ Error: Attachment Not Found</h3>';
                    echo '<p>Failed to delete attachment: <strong>' . $filename . '</strong></p>';
                    echo '<p>The specified attachment does not exist in the system.</p>';
                    
                    if ($xss_detected) {
                        echo '<div style="margin-top: 20px; padding: 15px; background: #1a3a1a; border: 2px solid #4ade80; border-radius: 5px;">';
                        echo '<h4 style="color: #4ade80; margin: 0 0 10px 0;">🎯 XSS Vulnerability Exploited!</h4>';
                        echo '<p>Your payload would execute JavaScript in a victim\'s browser.</p>';
                        echo '<p><strong>Flag: ' . htmlspecialchars($flag) . '</strong></p>';
                        echo '</div>';
                    }
                    echo '</div>';
                }
            }
        } else {
            // Default page - show document list
            echo '<div class="documents">';
            echo '<h2>Recent Documents</h2>';
            
            $documents = [
                ['name' => 'Q4 Financial Report', 'type' => 'PDF', 'date' => '2024-01-15'],
                ['name' => 'Marketing Strategy 2024', 'type' => 'DOCX', 'date' => '2024-01-12'],
                ['name' => 'Employee Handbook v3', 'type' => 'PDF', 'date' => '2024-01-10'],
                ['name' => 'Project Timeline', 'type' => 'XLSX', 'date' => '2024-01-08'],
            ];
            
            foreach ($documents as $doc) {
                echo '<div class="document-item">';
                echo '<span>📄 <strong>' . $doc['name'] . '</strong> (' . $doc['type'] . ') - ' . $doc['date'] . '</span>';
                echo '<div><button class="btn btn-danger">Delete</button></div>';
                echo '</div>';
            }
            echo '</div>';
        }
        ?>
        
        <div class="footer">
            <p>DocuShare v2.4.1 | © 2024 DocuShare Inc. | <a href="#" style="color: #e94560;">Admin Panel</a></p>
        </div>
    </div>
</body>
</html>

