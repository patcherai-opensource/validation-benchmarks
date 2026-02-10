package com.openmetadata.service.resources;

import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@RestController
@RequestMapping("/api/v1/users")
public class UsersResource {
    
    @GetMapping
    public ResponseEntity<Map<String, Object>> listUsers() {
        List<Map<String, Object>> users = new ArrayList<>();
        users.add(createUser("admin", "Admin User", "admin@openmetadata.org", true));
        users.add(createUser("user", "Regular User", "user@openmetadata.org", false));
        
        Map<String, Object> response = new HashMap<>();
        response.put("data", users);
        response.put("paging", Map.of("total", users.size()));
        
        return ResponseEntity.ok(response);
    }
    
    @GetMapping("/loggedInUser")
    public ResponseEntity<Map<String, Object>> getLoggedInUser(Authentication authentication) {
        String username = authentication.getName();
        boolean isAdmin = authentication.getAuthorities().stream()
            .anyMatch(a -> a.getAuthority().equals("ROLE_ADMIN"));
        
        Map<String, Object> user = createUser(username, username, username + "@openmetadata.org", isAdmin);
        return ResponseEntity.ok(user);
    }
    
    private Map<String, Object> createUser(String name, String displayName, String email, boolean isAdmin) {
        Map<String, Object> user = new HashMap<>();
        user.put("id", UUID.randomUUID());
        user.put("name", name);
        user.put("displayName", displayName);
        user.put("email", email);
        user.put("isAdmin", isAdmin);
        return user;
    }
}
