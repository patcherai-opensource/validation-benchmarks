<?php
header('Content-Type: application/json');
echo json_encode([
    'openapi' => '3.0.0',
    'info' => [
        'title' => 'PredictML Inference API',
        'version' => '2.4.1',
        'description' => 'REST API for machine learning model inference'
    ],
    'paths' => [
        '/api/v1/health' => [
            'get' => [
                'summary' => 'Health check endpoint',
                'responses' => ['200' => ['description' => 'Service is healthy']]
            ]
        ],
        '/api/v1/models' => [
            'get' => [
                'summary' => 'List available models',
                'responses' => ['200' => ['description' => 'List of models']]
            ]
        ],
        '/api/v1/predict' => [
            'post' => [
                'summary' => 'Run model inference',
                'description' => 'Submit data for prediction. Accepts file uploads or URLs to remote resources.',
                'requestBody' => [
                    'content' => [
                        'multipart/form-data' => [
                            'schema' => [
                                'type' => 'object',
                                'properties' => [
                                    'model' => ['type' => 'string', 'description' => 'Model ID to use'],
                                    'image' => ['type' => 'string', 'format' => 'binary', 'description' => 'Image file or URL'],
                                    'text' => ['type' => 'string', 'description' => 'Text input for NLP models']
                                ]
                            ]
                        ],
                        'application/json' => [
                            'schema' => [
                                'type' => 'object',
                                'properties' => [
                                    'model' => ['type' => 'string'],
                                    'input_url' => ['type' => 'string', 'description' => 'URL to fetch input data from'],
                                    'text' => ['type' => 'string']
                                ]
                            ]
                        ]
                    ]
                ],
                'responses' => [
                    '200' => ['description' => 'Prediction result'],
                    '400' => ['description' => 'Invalid request'],
                    '500' => ['description' => 'Inference error']
                ]
            ]
        ]
    ]
]);
?>
