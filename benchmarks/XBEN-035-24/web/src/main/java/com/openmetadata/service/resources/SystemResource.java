package com.openmetadata.service.resources;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/system")
public class SystemResource {
    
    @GetMapping("/version")
    public ResponseEntity<Map<String, String>> getVersion() {
        Map<String, String> version = new HashMap<>();
        version.put("version", "1.2.3");
        version.put("revision", "abc123def");
        version.put("timestamp", "2024-01-15T10:30:00Z");
        return ResponseEntity.ok(version);
    }
    
    @GetMapping("/config")
    public ResponseEntity<Map<String, Object>> getConfig() {
        Map<String, Object> config = new HashMap<>();
        config.put("airflowServiceUrl", "http://localhost:8080");
        config.put("authenticationConfiguration", Map.of(
            "provider", "basic",
            "publicKeyUrls", new String[]{}
        ));
        config.put("authorizer", Map.of(
            "className", "org.openmetadata.service.security.DefaultAuthorizer",
            "enabled", true
        ));
        return ResponseEntity.ok(config);
    }
}
