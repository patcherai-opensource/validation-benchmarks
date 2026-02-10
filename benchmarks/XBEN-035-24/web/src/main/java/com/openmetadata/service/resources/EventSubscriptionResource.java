package com.openmetadata.service.resources;

import com.openmetadata.service.model.EventSubscription;
import com.openmetadata.service.model.FilteringRules;
import com.openmetadata.service.model.Rule;
import com.openmetadata.service.util.AlertUtil;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

@RestController
@RequestMapping("/api/v1/events/subscriptions")
public class EventSubscriptionResource {
    
    private final Map<UUID, EventSubscription> subscriptions = new ConcurrentHashMap<>();
    
    @GetMapping
    public ResponseEntity<List<EventSubscription>> listSubscriptions() {
        return ResponseEntity.ok(new ArrayList<>(subscriptions.values()));
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<EventSubscription> getSubscription(@PathVariable UUID id) {
        EventSubscription subscription = subscriptions.get(id);
        if (subscription == null) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(subscription);
    }
    
    @PutMapping
    public ResponseEntity<?> createOrUpdateEventSubscription(@RequestBody EventSubscription subscription) {
        validateFilterRules(subscription);
        
        if (subscription.getId() == null) {
            subscription.setId(UUID.randomUUID());
        }
        
        subscriptions.put(subscription.getId(), subscription);
        
        Map<String, Object> response = new HashMap<>();
        response.put("id", subscription.getId());
        response.put("name", subscription.getName());
        response.put("status", "created");
        
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }
    
    @PostMapping
    public ResponseEntity<?> createEventSubscription(@RequestBody EventSubscription subscription) {
        return createOrUpdateEventSubscription(subscription);
    }
    
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteSubscription(@PathVariable UUID id) {
        if (subscriptions.remove(id) == null) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.noContent().build();
    }
    
    @PostMapping("/validate")
    public ResponseEntity<?> validateSubscription(@RequestBody EventSubscription subscription) {
        Map<String, Object> response = new HashMap<>();
        FilteringRules filteringRules = subscription.getFilteringRules();
        if (filteringRules != null && filteringRules.getRules() != null) {
            List<Map<String, Object>> validationResults = new ArrayList<>();
            for (Rule rule : filteringRules.getRules()) {
                Map<String, Object> ruleResult = new HashMap<>();
                ruleResult.put("name", rule.getName());
                if (rule.getCondition() != null && !rule.getCondition().isEmpty()) {
                    try {
                        Object result = AlertUtil.evaluateExpressionWithResult(rule.getCondition());
                        ruleResult.put("valid", true);
                        ruleResult.put("result", String.valueOf(result));
                    } catch (Exception e) {
                        ruleResult.put("valid", false);
                        ruleResult.put("error", "Invalid expression");
                    }
                } else {
                    ruleResult.put("valid", true);
                    ruleResult.put("result", "empty");
                }
                validationResults.add(ruleResult);
            }
            response.put("rules", validationResults);
        }
        response.put("status", "validated");
        return ResponseEntity.ok(response);
    }
    
    private void validateFilterRules(EventSubscription subscription) {
        FilteringRules filteringRules = subscription.getFilteringRules();
        if (filteringRules != null && filteringRules.getRules() != null) {
            for (Rule rule : filteringRules.getRules()) {
                if (rule.getCondition() != null && !rule.getCondition().isEmpty()) {
                    AlertUtil.validateExpression(rule.getCondition(), Boolean.class);
                }
            }
        }
    }
}
