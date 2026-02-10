package com.example.openmetadata.service;

import com.example.openmetadata.model.EventSubscription;
import com.example.openmetadata.model.Rule;
import org.springframework.stereotype.Repository;

import java.util.*;

@Repository
public class EventSubscriptionRepository {
    
    private final Map<String, EventSubscription> subscriptions = new HashMap<>();
    
    /**
     * Prepares and validates the event subscription before storage.
     * This mimics the OpenMetadata pattern where validateFilterRules is called
     * BEFORE authorization checks, allowing code execution even for unauthorized users.
     */
    public EventSubscription prepareInternal(EventSubscription subscription) {
        // Validate filter rules BEFORE any authorization - this is the vulnerability
        validateFilterRules(subscription);
        
        // Generate ID if not present
        if (subscription.getId() == null) {
            subscription.setId(UUID.randomUUID().toString());
        }
        
        return subscription;
    }
    
    /**
     * Validates filter rules by evaluating SpEL expressions.
     * VULNERABLE: Evaluates user-controlled expressions without sanitization.
     */
    private void validateFilterRules(EventSubscription subscription) {
        if (subscription.getFilteringRules() != null && 
            subscription.getFilteringRules().getRules() != null) {
            
            for (Rule rule : subscription.getFilteringRules().getRules()) {
                if (rule.getCondition() != null && !rule.getCondition().isEmpty()) {
                    // VULNERABLE: Directly evaluates user-provided SpEL expression
                    AlertUtil.validateExpression(rule.getCondition(), Boolean.class);
                }
            }
        }
    }
    
    public EventSubscription save(EventSubscription subscription) {
        subscriptions.put(subscription.getId(), subscription);
        return subscription;
    }
    
    public Optional<EventSubscription> findById(String id) {
        return Optional.ofNullable(subscriptions.get(id));
    }
    
    public List<EventSubscription> findAll() {
        return new ArrayList<>(subscriptions.values());
    }
    
    public void deleteById(String id) {
        subscriptions.remove(id);
    }
}
