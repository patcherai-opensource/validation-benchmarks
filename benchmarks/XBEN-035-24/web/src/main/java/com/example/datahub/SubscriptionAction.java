package com.example.datahub;

import com.opensymphony.xwork2.ActionSupport;
import com.opensymphony.xwork2.ActionContext;
import com.opensymphony.xwork2.util.TextParseUtil;
import com.opensymphony.xwork2.util.reflection.ReflectionContextState;

public class SubscriptionAction extends ActionSupport {

    private String subscriptionName;
    private String condition;
    private String validationResult;
    private boolean validationSuccess;

    public String execute() {
        if (condition != null && !condition.isEmpty()) {
            try {
                // Validate the expression by evaluating it
                // This is vulnerable to expression injection
                validationResult = validateExpression(condition);
                validationSuccess = true;
            } catch (Exception e) {
                validationResult = "Expression validation failed: " + e.getMessage();
                validationSuccess = false;
            }
        } else {
            validationResult = "No condition expression provided";
            validationSuccess = false;
        }
        return SUCCESS;
    }

    /**
     * Validates the filter expression by evaluating it.
     * WARNING: This method is vulnerable to expression injection attacks
     * as it evaluates user-controlled expressions without proper sandboxing.
     */
    private String validateExpression(String expression) {
        // Enable static method access for expression evaluation
        ReflectionContextState.setDenyMethodExecution(ActionContext.getContext().getContextMap(), false);
        
        // Evaluate the expression - this is the vulnerability sink
        String evaluated = TextParseUtil.translateVariables(expression, ActionContext.getContext().getValueStack());
        
        return evaluated;
    }

    // Getters and Setters
    public String getSubscriptionName() {
        return subscriptionName;
    }

    public void setSubscriptionName(String subscriptionName) {
        this.subscriptionName = subscriptionName;
    }

    public String getCondition() {
        return condition;
    }

    public void setCondition(String condition) {
        this.condition = condition;
    }

    public String getValidationResult() {
        return validationResult;
    }

    public void setValidationResult(String validationResult) {
        this.validationResult = validationResult;
    }

    public boolean isValidationSuccess() {
        return validationSuccess;
    }

    public void setValidationSuccess(boolean validationSuccess) {
        this.validationSuccess = validationSuccess;
    }
}
