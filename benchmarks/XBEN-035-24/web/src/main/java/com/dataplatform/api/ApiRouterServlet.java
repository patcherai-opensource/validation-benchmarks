package com.dataplatform.api;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.io.BufferedReader;
import java.io.PrintWriter;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import com.google.gson.Gson;
import com.google.gson.JsonObject;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.dataplatform.util.AlertUtil;

public class ApiRouterServlet extends HttpServlet {
    
    private static final Gson gson = new Gson();
    private static final Map<String, String> tokenStore = new ConcurrentHashMap<>();
    private static final Map<String, JsonObject> subscriptions = new ConcurrentHashMap<>();
    private static final Map<String, JsonObject> tables = new ConcurrentHashMap<>();
    private static final Map<String, JsonObject> databases = new ConcurrentHashMap<>();
    private static final Map<String, JsonObject> pipelines = new ConcurrentHashMap<>();
    
    static {
        // Initialize authentication tokens
        tokenStore.put("admin", "admin_token_2024");
        tokenStore.put("analyst", "analyst_token_2024");
        tokenStore.put("viewer", "viewer_token_2024");
        
        // Sample tables metadata
        JsonObject table1 = new JsonObject();
        table1.addProperty("id", "tbl-001");
        table1.addProperty("name", "customer_profiles");
        table1.addProperty("database", "analytics_db");
        table1.addProperty("owner", "data_team");
        table1.addProperty("columns", 15);
        table1.addProperty("rowCount", 2500000);
        tables.put("tbl-001", table1);
        
        JsonObject table2 = new JsonObject();
        table2.addProperty("id", "tbl-002");
        table2.addProperty("name", "sales_transactions");
        table2.addProperty("database", "warehouse_db");
        table2.addProperty("owner", "sales_team");
        table2.addProperty("columns", 22);
        table2.addProperty("rowCount", 15000000);
        tables.put("tbl-002", table2);
        
        JsonObject table3 = new JsonObject();
        table3.addProperty("id", "tbl-003");
        table3.addProperty("name", "product_catalog");
        table3.addProperty("database", "warehouse_db");
        table3.addProperty("owner", "product_team");
        table3.addProperty("columns", 8);
        table3.addProperty("rowCount", 50000);
        tables.put("tbl-003", table3);
        
        // Sample databases
        JsonObject db1 = new JsonObject();
        db1.addProperty("id", "db-001");
        db1.addProperty("name", "analytics_db");
        db1.addProperty("type", "PostgreSQL");
        db1.addProperty("status", "active");
        databases.put("db-001", db1);
        
        JsonObject db2 = new JsonObject();
        db2.addProperty("id", "db-002");
        db2.addProperty("name", "warehouse_db");
        db2.addProperty("type", "Snowflake");
        db2.addProperty("status", "active");
        databases.put("db-002", db2);
        
        // Sample pipelines
        JsonObject pipe1 = new JsonObject();
        pipe1.addProperty("id", "pipe-001");
        pipe1.addProperty("name", "ETL_CustomerData");
        pipe1.addProperty("status", "running");
        pipe1.addProperty("schedule", "0 0 * * *");
        pipelines.put("pipe-001", pipe1);
    }
    
    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) 
            throws ServletException, IOException {
        String path = req.getPathInfo();
        resp.setContentType("application/json");
        PrintWriter out = resp.getWriter();
        
        if (path == null || path.equals("/")) {
            JsonObject info = new JsonObject();
            info.addProperty("service", "DataPlatform Metadata Service");
            info.addProperty("version", "1.2.3");
            info.addProperty("status", "running");
            out.print(gson.toJson(info));
            return;
        }
        
        // Health endpoint - no auth
        if (path.equals("/v1/system/health")) {
            JsonObject health = new JsonObject();
            health.addProperty("status", "healthy");
            health.addProperty("database", "connected");
            health.addProperty("uptime", System.currentTimeMillis());
            out.print(gson.toJson(health));
            return;
        }
        
        // Version endpoint - no auth
        if (path.equals("/v1/system/version")) {
            JsonObject version = new JsonObject();
            version.addProperty("version", "1.2.3");
            version.addProperty("revision", "b847e9f");
            version.addProperty("timestamp", "2024-01-15T10:30:00Z");
            out.print(gson.toJson(version));
            return;
        }
        
        // Config endpoint - no auth
        if (path.equals("/v1/system/config")) {
            JsonObject config = new JsonObject();
            config.addProperty("authEnabled", true);
            config.addProperty("authProvider", "basic");
            config.addProperty("jwtTokenExpiry", 3600);
            config.addProperty("expressionEngine", "spel");
            out.print(gson.toJson(config));
            return;
        }
        
        // Protected endpoints require auth
        String authHeader = req.getHeader("Authorization");
        if (!isValidAuth(authHeader)) {
            resp.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            JsonObject error = new JsonObject();
            error.addProperty("error", "Unauthorized");
            error.addProperty("message", "Valid authorization token required. Use POST /api/v1/users/login to authenticate.");
            out.print(gson.toJson(error));
            return;
        }
        
        // Tables API
        if (path.equals("/v1/tables")) {
            JsonArray arr = new JsonArray();
            tables.values().forEach(arr::add);
            JsonObject result = new JsonObject();
            result.add("data", arr);
            result.addProperty("paging", "none");
            out.print(gson.toJson(result));
            return;
        }
        
        if (path.startsWith("/v1/tables/")) {
            String tableId = path.substring("/v1/tables/".length());
            JsonObject table = tables.get(tableId);
            if (table != null) {
                out.print(gson.toJson(table));
            } else {
                resp.setStatus(HttpServletResponse.SC_NOT_FOUND);
                JsonObject err = new JsonObject();
                err.addProperty("error", "Table not found");
                out.print(gson.toJson(err));
            }
            return;
        }
        
        // Databases API
        if (path.equals("/v1/databases")) {
            JsonArray arr = new JsonArray();
            databases.values().forEach(arr::add);
            JsonObject result = new JsonObject();
            result.add("data", arr);
            out.print(gson.toJson(result));
            return;
        }
        
        // Pipelines API (decoy)
        if (path.equals("/v1/pipelines")) {
            JsonArray arr = new JsonArray();
            pipelines.values().forEach(arr::add);
            JsonObject result = new JsonObject();
            result.add("data", arr);
            out.print(gson.toJson(result));
            return;
        }
        
        // Subscriptions API (GET)
        if (path.equals("/v1/events/subscriptions")) {
            JsonArray arr = new JsonArray();
            subscriptions.values().forEach(arr::add);
            JsonObject result = new JsonObject();
            result.add("data", arr);
            result.addProperty("total", subscriptions.size());
            out.print(gson.toJson(result));
            return;
        }
        
        if (path.startsWith("/v1/events/subscriptions/")) {
            String subId = path.substring("/v1/events/subscriptions/".length());
            JsonObject sub = subscriptions.get(subId);
            if (sub != null) {
                out.print(gson.toJson(sub));
            } else {
                resp.setStatus(HttpServletResponse.SC_NOT_FOUND);
                JsonObject err = new JsonObject();
                err.addProperty("error", "Subscription not found");
                out.print(gson.toJson(err));
            }
            return;
        }
        
        // Users API
        if (path.equals("/v1/users")) {
            JsonArray users = new JsonArray();
            JsonObject user1 = new JsonObject();
            user1.addProperty("name", "admin");
            user1.addProperty("email", "admin@dataplatform.local");
            user1.addProperty("role", "Admin");
            users.add(user1);
            JsonObject user2 = new JsonObject();
            user2.addProperty("name", "analyst");
            user2.addProperty("email", "analyst@dataplatform.local");
            user2.addProperty("role", "DataConsumer");
            users.add(user2);
            JsonObject user3 = new JsonObject();
            user3.addProperty("name", "viewer");
            user3.addProperty("email", "viewer@dataplatform.local");
            user3.addProperty("role", "Viewer");
            users.add(user3);
            JsonObject result = new JsonObject();
            result.add("data", users);
            out.print(gson.toJson(result));
            return;
        }
        
        // Lineage API (decoy)
        if (path.equals("/v1/lineage")) {
            JsonObject result = new JsonObject();
            result.addProperty("nodes", 45);
            result.addProperty("edges", 78);
            result.addProperty("status", "computed");
            out.print(gson.toJson(result));
            return;
        }
        
        resp.setStatus(HttpServletResponse.SC_NOT_FOUND);
        JsonObject err = new JsonObject();
        err.addProperty("error", "Endpoint not found");
        err.addProperty("path", path);
        out.print(gson.toJson(err));
    }
    
    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) 
            throws ServletException, IOException {
        String path = req.getPathInfo();
        resp.setContentType("application/json");
        PrintWriter out = resp.getWriter();
        
        // Login endpoint - no auth required
        if (path != null && path.equals("/v1/users/login")) {
            String body = readBody(req);
            JsonObject creds = gson.fromJson(body, JsonObject.class);
            String username = creds.has("email") ? creds.get("email").getAsString().split("@")[0] : "";
            String password = creds.has("password") ? creds.get("password").getAsString() : "";
            
            if (tokenStore.containsKey(username) && isValidPassword(username, password)) {
                JsonObject result = new JsonObject();
                result.addProperty("accessToken", tokenStore.get(username));
                result.addProperty("tokenType", "Bearer");
                result.addProperty("expiresIn", 3600);
                out.print(gson.toJson(result));
            } else {
                resp.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
                JsonObject err = new JsonObject();
                err.addProperty("error", "Invalid credentials");
                err.addProperty("message", "Check email and password");
                out.print(gson.toJson(err));
            }
            return;
        }
        
        // All other POST endpoints require auth
        String authHeader = req.getHeader("Authorization");
        if (!isValidAuth(authHeader)) {
            resp.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            JsonObject error = new JsonObject();
            error.addProperty("error", "Unauthorized");
            error.addProperty("message", "Valid authorization token required");
            out.print(gson.toJson(error));
            return;
        }
        
        resp.setStatus(HttpServletResponse.SC_METHOD_NOT_ALLOWED);
        JsonObject err = new JsonObject();
        err.addProperty("error", "Method not allowed for this endpoint");
        out.print(gson.toJson(err));
    }
    
    @Override
    protected void doPut(HttpServletRequest req, HttpServletResponse resp) 
            throws ServletException, IOException {
        String path = req.getPathInfo();
        resp.setContentType("application/json");
        PrintWriter out = resp.getWriter();
        
        String authHeader = req.getHeader("Authorization");
        if (!isValidAuth(authHeader)) {
            resp.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            JsonObject error = new JsonObject();
            error.addProperty("error", "Unauthorized");
            error.addProperty("message", "Valid authorization token required");
            out.print(gson.toJson(error));
            return;
        }
        
        // Event Subscriptions - CREATE/UPDATE (VULNERABLE ENDPOINT)
        if (path != null && path.equals("/v1/events/subscriptions")) {
            String body = readBody(req);
            try {
                JsonObject subscription = gson.fromJson(body, JsonObject.class);
                
                // Validate required fields
                if (!subscription.has("name") || !subscription.has("alertType")) {
                    resp.setStatus(HttpServletResponse.SC_BAD_REQUEST);
                    JsonObject err = new JsonObject();
                    err.addProperty("error", "Missing required fields: name, alertType");
                    out.print(gson.toJson(err));
                    return;
                }
                
                JsonArray validationResults = new JsonArray();
                
                // Process filter rules - VULNERABLE CODE PATH
                // Expression validation happens BEFORE authorization checks
                if (subscription.has("filteringRules")) {
                    JsonObject filteringRules = subscription.getAsJsonObject("filteringRules");
                    if (filteringRules.has("rules")) {
                        JsonArray rules = filteringRules.getAsJsonArray("rules");
                        for (JsonElement ruleElem : rules) {
                            JsonObject rule = ruleElem.getAsJsonObject();
                            if (rule.has("condition")) {
                                String condition = rule.get("condition").getAsString();
                                String ruleName = rule.has("name") ? rule.get("name").getAsString() : "unnamed";
                                
                                // VULNERABLE: Evaluates SpEL expression without restriction
                                // The result is included in the response for "debugging"
                                String validationResult = AlertUtil.validateExpression(condition, Boolean.class);
                                
                                JsonObject ruleValidation = new JsonObject();
                                ruleValidation.addProperty("rule", ruleName);
                                ruleValidation.addProperty("condition", condition);
                                ruleValidation.addProperty("validationResult", validationResult);
                                validationResults.add(ruleValidation);
                            }
                        }
                    }
                }
                
                // Generate ID and store
                String id = "sub-" + System.currentTimeMillis();
                subscription.addProperty("id", id);
                subscription.addProperty("status", "active");
                subscription.addProperty("createdAt", new Date().toString());
                subscriptions.put(id, subscription);
                
                // Build response with validation results
                JsonObject response = new JsonObject();
                response.addProperty("id", id);
                response.addProperty("status", "created");
                response.add("subscription", subscription);
                if (validationResults.size() > 0) {
                    response.add("ruleValidation", validationResults);
                }
                
                resp.setStatus(HttpServletResponse.SC_CREATED);
                out.print(gson.toJson(response));
                
            } catch (Exception e) {
                resp.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
                JsonObject err = new JsonObject();
                err.addProperty("error", "Failed to process subscription");
                err.addProperty("details", e.getMessage());
                out.print(gson.toJson(err));
            }
            return;
        }
        
        // Table update (decoy)
        if (path != null && path.startsWith("/v1/tables/")) {
            String tableId = path.substring("/v1/tables/".length());
            String body = readBody(req);
            JsonObject update = gson.fromJson(body, JsonObject.class);
            
            if (tables.containsKey(tableId)) {
                JsonObject table = tables.get(tableId);
                for (String key : update.keySet()) {
                    table.add(key, update.get(key));
                }
                out.print(gson.toJson(table));
            } else {
                resp.setStatus(HttpServletResponse.SC_NOT_FOUND);
                JsonObject err = new JsonObject();
                err.addProperty("error", "Table not found");
                out.print(gson.toJson(err));
            }
            return;
        }
        
        resp.setStatus(HttpServletResponse.SC_NOT_FOUND);
        JsonObject err = new JsonObject();
        err.addProperty("error", "Endpoint not found");
        out.print(gson.toJson(err));
    }
    
    @Override
    protected void doDelete(HttpServletRequest req, HttpServletResponse resp) 
            throws ServletException, IOException {
        String path = req.getPathInfo();
        resp.setContentType("application/json");
        PrintWriter out = resp.getWriter();
        
        String authHeader = req.getHeader("Authorization");
        if (!isValidAuth(authHeader)) {
            resp.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            JsonObject error = new JsonObject();
            error.addProperty("error", "Unauthorized");
            out.print(gson.toJson(error));
            return;
        }
        
        if (path != null && path.startsWith("/v1/events/subscriptions/")) {
            String subId = path.substring("/v1/events/subscriptions/".length());
            if (subscriptions.remove(subId) != null) {
                resp.setStatus(HttpServletResponse.SC_NO_CONTENT);
            } else {
                resp.setStatus(HttpServletResponse.SC_NOT_FOUND);
                JsonObject err = new JsonObject();
                err.addProperty("error", "Subscription not found");
                out.print(gson.toJson(err));
            }
            return;
        }
        
        resp.setStatus(HttpServletResponse.SC_NOT_FOUND);
    }
    
    private boolean isValidAuth(String authHeader) {
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            return false;
        }
        String token = authHeader.substring(7);
        return tokenStore.values().contains(token);
    }
    
    private boolean isValidPassword(String username, String password) {
        Map<String, String> passwords = new HashMap<>();
        passwords.put("admin", "admin123");
        passwords.put("analyst", "analyst2024");
        passwords.put("viewer", "viewer2024");
        return password.equals(passwords.get(username));
    }
    
    private String readBody(HttpServletRequest req) throws IOException {
        StringBuilder sb = new StringBuilder();
        BufferedReader reader = req.getReader();
        String line;
        while ((line = reader.readLine()) != null) {
            sb.append(line);
        }
        return sb.toString();
    }
}
