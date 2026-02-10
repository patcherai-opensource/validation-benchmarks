package com.example.openmetadata.controller;

import com.example.openmetadata.service.AlertUtil;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/**
 * Test endpoint for expression validation (for debugging/demo purposes).
 * This endpoint directly evaluates SpEL expressions and returns the result.
 */
@RestController
@RequestMapping("/api/v1/test")
public class ExpressionTestController {
    
    /**
     * Test endpoint that evaluates a SpEL expression and returns the result.
     * VULNERABLE: Directly evaluates user-provided SpEL expressions.
     * 
     * Example payloads:
     * - Simple: 1+1
     * - Read file: new java.util.Scanner(new java.io.File('/tmp/flag')).useDelimiter('\\A').next()
     * - Execute command: T(java.lang.Runtime).getRuntime().exec('id')
     */
    @PostMapping("/expression")
    public ResponseEntity<?> testExpression(@RequestBody Map<String, String> request) {
        String expression = request.get("expression");
        if (expression == null || expression.isEmpty()) {
            return ResponseEntity.badRequest().body(Map.of(
                "status", "error",
                "message", "Expression is required"
            ));
        }
        
        String result = AlertUtil.validateAndGetResult(expression);
        return ResponseEntity.ok(Map.of(
            "status", "success",
            "expression", expression,
            "result", result
        ));
    }
}
