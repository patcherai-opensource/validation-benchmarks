package com.assetmgr.servlet;

import com.assetmgr.model.Asset;
import com.assetmgr.model.AssetStore;
import com.google.gson.Gson;
import org.apache.commons.beanutils.PropertyUtils;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

@WebServlet("/api/v1/inspect")
public class AssetPropertyServlet extends HttpServlet {
    private final Gson gson = new Gson();

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        response.setContentType("application/json");
        response.setCharacterEncoding("UTF-8");

        String assetId = request.getParameter("id");
        String field = request.getParameter("field");

        if (assetId == null || assetId.isEmpty()) {
            sendError(response, HttpServletResponse.SC_BAD_REQUEST, "Parameter 'id' is required");
            return;
        }

        Asset asset = AssetStore.getInstance().getAsset(assetId);
        if (asset == null) {
            sendError(response, HttpServletResponse.SC_NOT_FOUND, "Asset not found");
            return;
        }

        if (field == null || field.isEmpty()) {
            sendError(response, HttpServletResponse.SC_BAD_REQUEST, "Parameter 'field' is required");
            return;
        }

        try {
            Object value = PropertyUtils.getProperty(asset, field);
            Map<String, Object> result = new HashMap<>();
            result.put("id", assetId);
            result.put("field", field);
            result.put("value", value != null ? value.toString() : null);
            result.put("type", value != null ? value.getClass().getSimpleName() : "null");
            response.getWriter().write(gson.toJson(result));
        } catch (Exception e) {
            sendError(response, HttpServletResponse.SC_BAD_REQUEST,
                    "Unable to resolve property: " + field);
        }
    }

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        response.setContentType("application/json");
        response.setCharacterEncoding("UTF-8");

        String assetId = request.getParameter("id");
        String field = request.getParameter("field");
        String value = request.getParameter("value");

        if (assetId == null || assetId.isEmpty()) {
            sendError(response, HttpServletResponse.SC_BAD_REQUEST, "Parameter 'id' is required");
            return;
        }

        Asset asset = AssetStore.getInstance().getAsset(assetId);
        if (asset == null) {
            sendError(response, HttpServletResponse.SC_NOT_FOUND, "Asset not found");
            return;
        }

        if (field == null || field.isEmpty()) {
            sendError(response, HttpServletResponse.SC_BAD_REQUEST, "Parameter 'field' is required");
            return;
        }

        if (value == null) {
            sendError(response, HttpServletResponse.SC_BAD_REQUEST, "Parameter 'value' is required");
            return;
        }

        try {
            PropertyUtils.setProperty(asset, field, value);
            Map<String, Object> result = new HashMap<>();
            result.put("id", assetId);
            result.put("field", field);
            result.put("value", value);
            result.put("updated", true);
            response.getWriter().write(gson.toJson(result));
        } catch (Exception e) {
            sendError(response, HttpServletResponse.SC_BAD_REQUEST,
                    "Unable to set property: " + field);
        }
    }

    private void sendError(HttpServletResponse response, int status, String message) throws IOException {
        response.setStatus(status);
        Map<String, String> error = new HashMap<>();
        error.put("error", message);
        response.getWriter().write(gson.toJson(error));
    }
}
