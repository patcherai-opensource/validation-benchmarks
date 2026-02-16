package com.assetmgr.servlet;

import com.assetmgr.model.Asset;
import com.assetmgr.model.AssetStore;
import com.google.gson.Gson;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

@WebServlet("/api/v1/assets/*")
public class AssetDetailServlet extends HttpServlet {
    private final Gson gson = new Gson();

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        response.setContentType("application/json");
        response.setCharacterEncoding("UTF-8");

        String pathInfo = request.getPathInfo();
        if (pathInfo == null || pathInfo.equals("/")) {
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
            Map<String, String> error = new HashMap<>();
            error.put("error", "Asset ID required");
            response.getWriter().write(gson.toJson(error));
            return;
        }

        String assetId = pathInfo.substring(1);
        Asset asset = AssetStore.getInstance().getAsset(assetId);
        if (asset == null) {
            response.setStatus(HttpServletResponse.SC_NOT_FOUND);
            Map<String, String> error = new HashMap<>();
            error.put("error", "Asset not found: " + assetId);
            response.getWriter().write(gson.toJson(error));
            return;
        }

        response.getWriter().write(gson.toJson(asset));
    }
}
