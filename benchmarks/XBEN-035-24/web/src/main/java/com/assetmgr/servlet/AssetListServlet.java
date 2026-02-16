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
import java.util.Collection;

@WebServlet("/api/v1/assets")
public class AssetListServlet extends HttpServlet {
    private final Gson gson = new Gson();

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        response.setContentType("application/json");
        response.setCharacterEncoding("UTF-8");

        Collection<Asset> assets = AssetStore.getInstance().getAllAssets();
        response.getWriter().write(gson.toJson(assets));
    }
}
