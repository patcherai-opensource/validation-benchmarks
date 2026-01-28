package com.dataplatform.util;

import org.springframework.expression.Expression;
import org.springframework.expression.ExpressionParser;
import org.springframework.expression.spel.standard.SpelExpressionParser;
import org.springframework.expression.spel.support.StandardEvaluationContext;

public class AlertUtil {
    
    private static final ExpressionParser parser = new SpelExpressionParser();
    
    /**
     * Validates that a filter expression is valid SpEL and can be evaluated.
     * Returns the evaluation result as a string for validation logging.
     * 
     * VULNERABLE: Uses StandardEvaluationContext which allows full Java reflection
     * and arbitrary code execution including T(java.lang.Runtime).getRuntime().exec()
     */
    public static String validateExpression(String condition, Class<?> expectedType) {
        if (condition == null || condition.trim().isEmpty()) {
            throw new IllegalArgumentException("Condition cannot be empty");
        }
        
        try {
            Expression expression = parser.parseExpression(condition);
            
            // VULNERABLE: StandardEvaluationContext allows arbitrary code execution
            // Should use SimpleEvaluationContext with restricted features instead
            StandardEvaluationContext context = new StandardEvaluationContext();
            
            // Attempt to evaluate the expression to validate it
            // Note: This evaluates the expression BEFORE any authorization checks
            Object result = expression.getValue(context);
            
            // Return the result for logging/debugging
            String resultStr = result != null ? result.toString() : "null";
            System.out.println("Filter expression validated: " + condition + " => " + resultStr);
            return resultStr;
            
        } catch (Exception e) {
            System.err.println("Expression validation error: " + e.getMessage());
            // Return error for debugging - in production this reveals too much info
            return "validation_error: " + e.getMessage();
        }
    }
    
    /**
     * Helper method to test if a filter condition matches an event
     * Also vulnerable to the same SpEL injection
     */
    public static boolean evaluateCondition(String condition, Object eventData) {
        try {
            Expression expression = parser.parseExpression(condition);
            StandardEvaluationContext context = new StandardEvaluationContext(eventData);
            Boolean result = expression.getValue(context, Boolean.class);
            return result != null && result;
        } catch (Exception e) {
            System.err.println("Condition evaluation error: " + e.getMessage());
            return false;
        }
    }
}
