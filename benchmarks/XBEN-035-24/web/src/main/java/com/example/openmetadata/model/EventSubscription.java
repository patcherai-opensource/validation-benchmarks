package com.example.openmetadata.model;

import java.util.List;

public class EventSubscription {
    private String id;
    private String name;
    private String displayName;
    private String alertType;
    private FilteringRules filteringRules;
    private String subscriptionType;
    private boolean enabled;

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    
    public String getDisplayName() { return displayName; }
    public void setDisplayName(String displayName) { this.displayName = displayName; }
    
    public String getAlertType() { return alertType; }
    public void setAlertType(String alertType) { this.alertType = alertType; }
    
    public FilteringRules getFilteringRules() { return filteringRules; }
    public void setFilteringRules(FilteringRules filteringRules) { this.filteringRules = filteringRules; }
    
    public String getSubscriptionType() { return subscriptionType; }
    public void setSubscriptionType(String subscriptionType) { this.subscriptionType = subscriptionType; }
    
    public boolean isEnabled() { return enabled; }
    public void setEnabled(boolean enabled) { this.enabled = enabled; }
}
