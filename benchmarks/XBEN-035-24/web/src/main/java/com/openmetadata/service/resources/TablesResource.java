package com.openmetadata.service.resources;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@RestController
@RequestMapping("/api/v1/tables")
public class TablesResource {
    
    @GetMapping
    public ResponseEntity<Map<String, Object>> listTables(
            @RequestParam(defaultValue = "10") int limit,
            @RequestParam(defaultValue = "0") int offset) {
        
        List<Map<String, Object>> tables = new ArrayList<>();
        tables.add(createTable("users", "dim_users", "sample_data.ecommerce"));
        tables.add(createTable("orders", "fact_orders", "sample_data.ecommerce"));
        tables.add(createTable("products", "dim_products", "sample_data.ecommerce"));
        
        Map<String, Object> response = new HashMap<>();
        response.put("data", tables);
        response.put("paging", Map.of("total", tables.size()));
        
        return ResponseEntity.ok(response);
    }
    
    @GetMapping("/{fqn}")
    public ResponseEntity<Map<String, Object>> getTable(@PathVariable String fqn) {
        Map<String, Object> table = new HashMap<>();
        table.put("id", UUID.randomUUID());
        table.put("name", fqn.substring(fqn.lastIndexOf('.') + 1));
        table.put("fullyQualifiedName", fqn);
        table.put("tableType", "Regular");
        
        return ResponseEntity.ok(table);
    }
    
    private Map<String, Object> createTable(String name, String displayName, String schema) {
        Map<String, Object> table = new HashMap<>();
        table.put("id", UUID.randomUUID());
        table.put("name", name);
        table.put("displayName", displayName);
        table.put("fullyQualifiedName", schema + "." + name);
        table.put("tableType", "Regular");
        return table;
    }
}
