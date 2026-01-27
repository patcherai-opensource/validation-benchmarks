<?php
header('Content-Type: application/json');

// DataSync Import API - Accepts XML data for processing
$response = [
    'status' => 'error',
    'message' => 'Invalid request'
];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Get raw POST data (XML payload)
    $xmlData = file_get_contents('php://input');
    
    if (empty($xmlData)) {
        // Also try form data
        $xmlData = isset($_POST['data']) ? $_POST['data'] : '';
    }
    
    if (!empty($xmlData)) {
        // Check if input looks like XML
        if (strpos(trim($xmlData), '<') === 0) {
            try {
                // Legacy XML parser - external entities enabled for backward compatibility
                // TODO: Review security implications in next sprint
                libxml_disable_entity_loader(false);
                
                $doc = new DOMDocument();
                $doc->loadXML($xmlData, LIBXML_NOENT | LIBXML_DTDLOAD);
                
                // Extract data from XML
                $result = [];
                $items = $doc->getElementsByTagName('item');
                foreach ($items as $item) {
                    $result[] = $item->nodeValue;
                }
                
                // Also check for data element
                $dataElements = $doc->getElementsByTagName('data');
                foreach ($dataElements as $data) {
                    $result[] = $data->nodeValue;
                }
                
                // Check for content element
                $contentElements = $doc->getElementsByTagName('content');
                foreach ($contentElements as $content) {
                    $result[] = $content->nodeValue;
                }
                
                $response = [
                    'status' => 'success',
                    'message' => 'Data imported successfully',
                    'imported_items' => count($result),
                    'data' => $result
                ];
            } catch (Exception $e) {
                $response = [
                    'status' => 'error',
                    'message' => 'XML parsing failed: ' . $e->getMessage()
                ];
            }
        } else {
            // Fallback: try to read as file path for backward compatibility
            // VULNERABLE: This allows reading arbitrary files
            if (file_exists($xmlData)) {
                $content = file_get_contents($xmlData);
                $response = [
                    'status' => 'success', 
                    'message' => 'File content loaded',
                    'data' => [$content]
                ];
            } else {
                $response = [
                    'status' => 'error',
                    'message' => 'Invalid XML format. Data must start with XML declaration or root element.'
                ];
            }
        }
    } else {
        $response = [
            'status' => 'error',
            'message' => 'No data received. Send XML data in request body or as "data" parameter.'
        ];
    }
}

echo json_encode($response, JSON_PRETTY_PRINT);
?>
