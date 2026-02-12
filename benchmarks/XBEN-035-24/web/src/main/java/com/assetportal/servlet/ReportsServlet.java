package com.assetportal.servlet;

import com.assetportal.model.Asset;
import com.assetportal.model.AssetCategory;
import com.assetportal.model.AssetStatus;
import com.assetportal.util.AssetRepository;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.Collection;
import java.util.HashMap;
import java.util.Map;

@WebServlet("/reports")
public class ReportsServlet extends HttpServlet {

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {

        Collection<Asset> assets = AssetRepository.getAll();

        Map<String, Integer> categoryCounts = new HashMap<>();
        Map<String, Integer> statusCounts = new HashMap<>();
        double totalValue = 0;

        for (Asset a : assets) {
            String cat = a.getCategory().getDisplayName();
            categoryCounts.put(cat, categoryCounts.getOrDefault(cat, 0) + 1);

            String st = a.getStatus().getLabel();
            statusCounts.put(st, statusCounts.getOrDefault(st, 0) + 1);

            totalValue += a.getPurchasePrice();
        }

        req.setAttribute("categoryCounts", categoryCounts);
        req.setAttribute("statusCounts", statusCounts);
        req.setAttribute("totalValue", totalValue);
        req.setAttribute("totalAssets", assets.size());

        req.getRequestDispatcher("/WEB-INF/views/reports.jsp").forward(req, resp);
    }
}
