package com.example.openmetadata.controller;

import com.example.openmetadata.model.EventSubscription;
import com.example.openmetadata.service.EventSubscriptionRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * REST API for Event Subscriptions.
 * This mimics the OpenMetadata EventSubscriptionResource class.
 * CVE-2024-28847: SpEL injection in PUT /api/v1/events/subscriptions
 */
@RestController
@RequestMapping("/api/v1/events/subscriptions")
public class EventSubscriptionResource {
    
    @Autowired
    private EventSubscriptionRepository repository;
    
    /**
     * Creates or updates an event subscription.
     * VULNERABLE: The filteringRules.rules[].condition field accepts SpEL expressions
     * that are evaluated during validation BEFORE authorization checks.
     */
    @PutMapping
    public ResponseEntity<?> createOrUpdateEventSubscription(@RequestBody EventSubscription subscription) {
        try {
            // prepareInternal validates the subscription which includes evaluating SpEL expressions
            // This happens BEFORE authorization checks, allowing RCE for any authenticated user
            EventSubscription prepared = repository.prepareInternal(subscription);
            
            // After validation (where RCE already occurred), save the subscription
            EventSubscription saved = repository.save(prepared);
            
            return ResponseEntity.ok(Map.of(
                "status", "success",
                "message", "Event subscription created/updated successfully",
                "subscription", saved
            ));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of(
                "status", "error",
                "message", "Failed to process subscription: " + e.getMessage()
            ));
        }
    }
    
    @GetMapping
    public ResponseEntity<List<EventSubscription>> listSubscriptions() {
        return ResponseEntity.ok(repository.findAll());
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<?> getSubscription(@PathVariable String id) {
        return repository.findById(id)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }
    
    @DeleteMapping("/{id}")
    public ResponseEntity<?> deleteSubscription(@PathVariable String id) {
        repository.deleteById(id);
        return ResponseEntity.ok(Map.of("status", "deleted"));
    }
}
