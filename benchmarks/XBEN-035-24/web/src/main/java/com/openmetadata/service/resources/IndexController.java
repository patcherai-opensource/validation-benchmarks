package com.openmetadata.service.resources;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;

@RestController
public class IndexController {
    
    @GetMapping("/")
    public ResponseEntity<Map<String, Object>> index() {
        Map<String, Object> response = new HashMap<>();
        response.put("name", "OpenMetadata");
        response.put("description", "Open standard for metadata");
        response.put("documentation", "https://docs.open-metadata.org");
        response.put("version", "1.2.3");
        return ResponseEntity.ok(response);
    }
    
    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        Map<String, String> health = new HashMap<>();
        health.put("status", "healthy");
        return ResponseEntity.ok(health);
    }
}
