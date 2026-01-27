<?php
header('Content-Type: application/json');

echo json_encode([
    "openapi" => "3.0.0",
    "info" => [
        "title" => "AppBuilder Security API",
        "version" => "1.0.0",
        "description" => "REST API for AppBuilder authentication and authorization"
    ],
    "paths" => [
        "/api/v1/security/login" => [
            "post" => [
                "summary" => "Authenticate user",
                "description" => "Login with username and password. Supports multiple authentication providers.",
                "requestBody" => [
                    "required" => true,
                    "content" => [
                        "application/json" => [
                            "schema" => [
                                "type" => "object",
                                "properties" => [
                                    "username" => ["type" => "string"],
                                    "password" => ["type" => "string"],
                                    "provider" => [
                                        "type" => "string",
                                        "enum" => ["db", "ldap"],
                                        "description" => "Authentication provider to use"
                                    ]
                                ],
                                "required" => ["username", "password"]
                            ]
                        ]
                    ]
                ],
                "responses" => [
                    "200" => [
                        "description" => "Authentication successful"
                    ],
                    "401" => [
                        "description" => "Invalid credentials"
                    ]
                ]
            ]
        ]
    ]
], JSON_PRETTY_PRINT);
?>
