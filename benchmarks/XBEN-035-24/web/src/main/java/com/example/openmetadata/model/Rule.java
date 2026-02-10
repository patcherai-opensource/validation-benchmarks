package com.example.openmetadata.model;

public class Rule {
    private String name;
    private String effect;
    private String condition;
    
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    
    public String getEffect() { return effect; }
    public void setEffect(String effect) { this.effect = effect; }
    
    public String getCondition() { return condition; }
    public void setCondition(String condition) { this.condition = condition; }
}
