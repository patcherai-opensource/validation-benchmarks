package com.assetportal.servlet;

import com.assetportal.model.Asset;
import com.assetportal.util.AssetRepository;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

@WebServlet("/asset")
public class AssetDetailServlet extends HttpServlet {

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {

        String idParam = req.getParameter("id");
        if (idParam == null || idParam.isEmpty()) {
            resp.sendRedirect(req.getContextPath() + "/dashboard");
            return;
        }

        try {
            int id = Integer.parseInt(idParam);
            Asset asset = AssetRepository.getById(id);

            if (asset == null) {
                resp.sendError(HttpServletResponse.SC_NOT_FOUND, "Asset not found");
                return;
            }

            req.setAttribute("asset", asset);
            req.getRequestDispatcher("/WEB-INF/views/asset-detail.jsp").forward(req, resp);
        } catch (NumberFormatException e) {
            resp.sendError(HttpServletResponse.SC_BAD_REQUEST, "Invalid asset ID");
        }
    }
}
