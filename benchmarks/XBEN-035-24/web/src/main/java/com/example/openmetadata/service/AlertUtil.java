package com.example.openmetadata.service;

import org.springframework.expression.Expression;
import org.springframework.expression.ExpressionParser;
import org.springframework.expression.spel.standard.SpelExpressionParser;
import org.springframework.expression.spel.support.StandardEvaluationContext;
import org.springframework.stereotype.Component;

/**
 * Utility class for validating alert filter expressions.
 * This is modeled after the vulnerable AlertUtil in OpenMetadata < 1.2.4
 * CVE-2024-28847: SpEL injection vulnerability
 */
@Component
public class AlertUtil {
    
    private static final ExpressionParser parser = new SpelExpressionParser();
    
    /**
     * Validates a SpEL expression by evaluating it.
     * VULNERABLE: This evaluates user-controlled SpEL expressions without restrictions,
     * allowing arbitrary code execution via expressions like:
     * T(java.lang.Runtime).getRuntime().exec('command')
     */
    public static <T> T validateExpression(String condition, Class<T> clz) {
        // Parse the SpEL expression
        Expression expression = parser.parseExpression(condition);
        
        // Create an evaluation context - VULNERABLE: no restrictions on what can be executed
        StandardEvaluationContext context = new StandardEvaluationContext();
        
        // Evaluate the expression - this is where arbitrary code execution occurs
        return expression.getValue(context, clz);
    }
    
    /**
     * Validates a condition and returns result as string for display
     */
    public static String validateAndGetResult(String condition) {
        try {
            Object result = validateExpression(condition, Object.class);
            if (result != null) {
                return result.toString();
            }
            return "Expression evaluated successfully (null result)";
        } catch (Exception e) {
            return "Expression validation failed: " + e.getMessage();
        }
    }
}
