<?php
header('Content-Type: application/json');

// DataSync Import API - Primary XML Import Endpoint
$response = [
    'status' => 'error',
    'message' => 'No data received.'
];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Get raw POST data
    $xmlData = file_get_contents('php://input');
    
    if (empty($xmlData)) {
        $xmlData = isset($_POST['xml']) ? $_POST['xml'] : '';
    }
    
    if (!empty($xmlData)) {
        try {
            // VULNERABLE: External entities enabled for "compatibility"
            libxml_disable_entity_loader(false);
            
            $doc = new DOMDocument();
            // Parse XML with external entities enabled
            $doc->loadXML($xmlData, LIBXML_NOENT | LIBXML_DTDLOAD);
            
            $results = [];
            
            // Process various element types
            $tagNames = ['record', 'entry', 'item', 'data', 'value', 'content', 'name', 'field'];
            foreach ($tagNames as $tagName) {
                $elements = $doc->getElementsByTagName($tagName);
                foreach ($elements as $element) {
                    $results[] = [
                        'tag' => $tagName,
                        'value' => $element->nodeValue
                    ];
                }
            }
            
            $response = [
                'status' => 'success',
                'message' => 'XML data processed successfully',
                'records_processed' => count($results),
                'results' => $results
            ];
            
        } catch (Exception $e) {
            $response = [
                'status' => 'error',
                'message' => 'XML processing error: ' . $e->getMessage()
            ];
        }
    } else {
        $response['message'] = 'No XML data provided. Send XML in request body.';
    }
}

echo json_encode($response, JSON_PRETTY_PRINT);
?>
