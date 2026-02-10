package com.openmetadata.service.model;

public class AlertsRuleEvaluator {
    
    private Object event;
    
    public AlertsRuleEvaluator(Object event) {
        this.event = event;
    }
    
    public Object getEvent() {
        return event;
    }
    
    public boolean matchAnySource(String... sources) {
        return true;
    }
    
    public boolean matchAnyOwnerName(String... owners) {
        return true;
    }
    
    public boolean matchAnyEntityId(String... ids) {
        return true;
    }
    
    public boolean matchAnyEntityFqn(String... fqns) {
        return true;
    }
}
