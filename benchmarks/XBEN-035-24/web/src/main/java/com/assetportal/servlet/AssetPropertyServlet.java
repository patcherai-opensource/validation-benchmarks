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

/**
 * REST-style endpoint for retrieving individual asset properties.
 * Used by the frontend for dynamic field rendering and export functionality.
 */
@WebServlet("/api/asset/property")
public class AssetPropertyServlet extends HttpServlet {

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {

        String idParam = req.getParameter("id");
        String field = req.getParameter("field");

        if (idParam == null || field == null || idParam.isEmpty() || field.isEmpty()) {
            sendJsonError(resp, HttpServletResponse.SC_BAD_REQUEST,
                    "Missing required parameters: id, field");
            return;
        }

        try {
            int id = Integer.parseInt(idParam);
            Asset asset = AssetRepository.getById(id);

            if (asset == null) {
                sendJsonError(resp, HttpServletResponse.SC_NOT_FOUND, "Asset not found");
                return;
            }

            Object value = PropertyUtils.getProperty(asset, field);

            resp.setContentType("application/json");
            resp.setCharacterEncoding("UTF-8");
            PrintWriter out = resp.getWriter();

            if (value == null) {
                out.print("{\"id\":" + id + ",\"field\":\"" + escapeJson(field) + "\",\"value\":null}");
            } else {
                out.print("{\"id\":" + id + ",\"field\":\"" + escapeJson(field) +
                        "\",\"value\":\"" + escapeJson(value.toString()) + "\"}");
            }
            out.flush();

        } catch (NumberFormatException e) {
            sendJsonError(resp, HttpServletResponse.SC_BAD_REQUEST, "Invalid asset ID format");
        } catch (NoSuchMethodException e) {
            sendJsonError(resp, HttpServletResponse.SC_BAD_REQUEST,
                    "Unknown property: " + field);
        } catch (Exception e) {
            sendJsonError(resp, HttpServletResponse.SC_INTERNAL_SERVER_ERROR,
                    "Error retrieving property");
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
