package com.assetportal.servlet;

import com.assetportal.model.Asset;
import com.assetportal.util.AssetRepository;
import org.apache.commons.beanutils.PropertyUtils;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.Enumeration;

/**
 * Handles property updates on asset records.
 * Accepts POST requests with property name/value pairs for dynamic field editing.
 */
@WebServlet("/api/asset/update")
public class AssetUpdateServlet extends HttpServlet {

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {

        String idParam = req.getParameter("id");

        if (idParam == null || idParam.isEmpty()) {
            sendJsonError(resp, HttpServletResponse.SC_BAD_REQUEST,
                    "Missing required parameter: id");
            return;
        }

        try {
            int id = Integer.parseInt(idParam);
            Asset asset = AssetRepository.getById(id);

            if (asset == null) {
                sendJsonError(resp, HttpServletResponse.SC_NOT_FOUND, "Asset not found");
                return;
            }

            int updated = 0;
            Enumeration<String> paramNames = req.getParameterNames();
            while (paramNames.hasMoreElements()) {
                String param = paramNames.nextElement();
                if ("id".equals(param)) continue;

                String value = req.getParameter(param);
                try {
                    PropertyUtils.setProperty(asset, param, value);
                    updated++;
                } catch (Exception e) {
                    // skip properties that can't be set
                }
            }

            resp.setContentType("application/json");
            resp.setCharacterEncoding("UTF-8");
            PrintWriter out = resp.getWriter();
            out.print("{\"id\":" + id + ",\"updated\":" + updated + ",\"status\":\"ok\"}");
            out.flush();

        } catch (NumberFormatException e) {
            sendJsonError(resp, HttpServletResponse.SC_BAD_REQUEST, "Invalid asset ID format");
        } catch (Exception e) {
            sendJsonError(resp, HttpServletResponse.SC_INTERNAL_SERVER_ERROR,
                    "Error updating property");
        }
    }

    private void sendJsonError(HttpServletResponse resp, int status, String message)
            throws IOException {
        resp.setStatus(status);
        resp.setContentType("application/json");
        resp.setCharacterEncoding("UTF-8");
        resp.getWriter().print("{\"error\":\"" + escapeJson(message) + "\"}");
    }

    private String escapeJson(String input) {
        if (input == null) return "";
        return input.replace("\\", "\\\\")
                     .replace("\"", "\\\"")
                     .replace("\n", "\\n")
                     .replace("\r", "\\r")
                     .replace("\t", "\\t");
    }
}
