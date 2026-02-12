<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<%@ taglib prefix="fmt" uri="http://java.sun.com/jsp/jstl/fmt" %>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Asset Portal - Dashboard</title>
    <link rel="stylesheet" href="${pageContext.request.contextPath}/css/style.css">
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand">
            <span class="logo">&#9881;</span> Asset Portal
        </div>
        <div class="nav-links">
            <a href="${pageContext.request.contextPath}/dashboard" class="active">Dashboard</a>
            <a href="${pageContext.request.contextPath}/reports">Reports</a>
        </div>
        <div class="nav-user">
            <span>admin@corp.local</span>
        </div>
    </nav>

    <div class="container">
        <div class="page-header">
            <h1>Asset Inventory</h1>
            <p class="subtitle">Tracking ${totalCount} assets across the organization</p>
        </div>

        <div class="stats-row">
            <div class="stat-card">
                <div class="stat-value">${totalCount}</div>
                <div class="stat-label">Total Assets</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">5</div>
                <div class="stat-label">Categories</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">2</div>
                <div class="stat-label">Locations</div>
            </div>
        </div>

        <table class="data-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Serial Number</th>
                    <th>Category</th>
                    <th>Status</th>
                    <th>Assigned To</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                <c:forEach var="asset" items="${assets}">
                <tr>
                    <td>${asset.id}</td>
                    <td>${asset.name}</td>
                    <td><code>${asset.serialNumber}</code></td>
                    <td><span class="badge badge-category">${asset.category.displayName}</span></td>
                    <td>
                        <c:choose>
                            <c:when test="${asset.status == 'ACTIVE'}">
                                <span class="badge badge-active">${asset.status.label}</span>
                            </c:when>
                            <c:when test="${asset.status == 'MAINTENANCE'}">
                                <span class="badge badge-maintenance">${asset.status.label}</span>
                            </c:when>
                            <c:when test="${asset.status == 'DECOMMISSIONED'}">
                                <span class="badge badge-decommissioned">${asset.status.label}</span>
                            </c:when>
                            <c:when test="${asset.status == 'RESERVED'}">
                                <span class="badge badge-reserved">${asset.status.label}</span>
                            </c:when>
                        </c:choose>
                    </td>
                    <td>${asset.assignedTo}</td>
                    <td>
                        <a href="${pageContext.request.contextPath}/asset?id=${asset.id}" class="btn btn-sm">View</a>
                    </td>
                </tr>
                </c:forEach>
            </tbody>
        </table>
    </div>

    <footer class="footer">
        <p>&copy; 2024 Corp IT Services - Asset Management Portal v3.2.1</p>
    </footer>
</body>
</html>
