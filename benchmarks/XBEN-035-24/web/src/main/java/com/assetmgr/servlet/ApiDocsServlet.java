package com.assetmgr.servlet;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.*;

@WebServlet("/api")
public class ApiDocsServlet extends HttpServlet {
    private final Gson gson = new GsonBuilder().setPrettyPrinting().create();

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        response.setContentType("application/json");
        response.setCharacterEncoding("UTF-8");

        Map<String, Object> docs = new LinkedHashMap<>();
        docs.put("name", "IT Asset Manager API");
        docs.put("version", "1.0.0");

        List<Map<String, Object>> endpoints = new ArrayList<>();

        Map<String, Object> listEndpoint = new LinkedHashMap<>();
        listEndpoint.put("method", "GET");
        listEndpoint.put("path", "/api/v1/assets");
        listEndpoint.put("description", "List all registered assets");
        endpoints.add(listEndpoint);

        Map<String, Object> detailEndpoint = new LinkedHashMap<>();
        detailEndpoint.put("method", "GET");
        detailEndpoint.put("path", "/api/v1/assets/{id}");
        detailEndpoint.put("description", "Get asset details by ID");
        endpoints.add(detailEndpoint);

        Map<String, Object> inspectGetEndpoint = new LinkedHashMap<>();
        inspectGetEndpoint.put("method", "GET");
        inspectGetEndpoint.put("path", "/api/v1/inspect");
        inspectGetEndpoint.put("description", "Inspect a specific asset property");
        Map<String, String> inspectGetParams = new LinkedHashMap<>();
        inspectGetParams.put("id", "Asset ID (e.g., AST-001)");
        inspectGetParams.put("field", "Property name to inspect (e.g., name, status, priority)");
        inspectGetEndpoint.put("parameters", inspectGetParams);
        endpoints.add(inspectGetEndpoint);

        Map<String, Object> inspectPostEndpoint = new LinkedHashMap<>();
        inspectPostEndpoint.put("method", "POST");
        inspectPostEndpoint.put("path", "/api/v1/inspect");
        inspectPostEndpoint.put("description", "Update a specific asset property");
        Map<String, String> inspectPostParams = new LinkedHashMap<>();
        inspectPostParams.put("id", "Asset ID");
        inspectPostParams.put("field", "Property name to update");
        inspectPostParams.put("value", "New value");
        inspectPostEndpoint.put("parameters", inspectPostParams);
        endpoints.add(inspectPostEndpoint);

        docs.put("endpoints", endpoints);

        response.getWriter().write(gson.toJson(docs));
    }
}
