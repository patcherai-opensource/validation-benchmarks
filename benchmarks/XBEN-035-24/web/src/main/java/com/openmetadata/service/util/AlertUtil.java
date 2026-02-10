package com.openmetadata.service.util;

import org.springframework.expression.Expression;
import org.springframework.expression.ExpressionParser;
import org.springframework.expression.spel.standard.SpelExpressionParser;
import org.springframework.expression.spel.support.StandardEvaluationContext;

public class AlertUtil {
    
    private static final ExpressionParser parser = new SpelExpressionParser();
    
    public static <T> void validateExpression(String condition, Class<T> clz) {
        Expression expression = parser.parseExpression(condition);
        StandardEvaluationContext context = new StandardEvaluationContext();
        expression.getValue(context, clz);
    }
    
    public static Object evaluateExpressionWithResult(String condition) {
        Expression expression = parser.parseExpression(condition);
        StandardEvaluationContext context = new StandardEvaluationContext();
        return expression.getValue(context);
    }
    
    public static boolean evaluateCondition(String condition) {
        try {
            Expression expression = parser.parseExpression(condition);
            StandardEvaluationContext context = new StandardEvaluationContext();
            Object result = expression.getValue(context);
            return result instanceof Boolean ? (Boolean) result : true;
        } catch (Exception e) {
            return false;
        }
    }
}
