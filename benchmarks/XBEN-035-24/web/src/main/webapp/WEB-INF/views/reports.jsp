<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<%@ taglib prefix="fmt" uri="http://java.sun.com/jsp/jstl/fmt" %>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Asset Portal - Reports</title>
    <link rel="stylesheet" href="${pageContext.request.contextPath}/css/style.css">
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand">
            <span class="logo">&#9881;</span> Asset Portal
        </div>
        <div class="nav-links">
            <a href="${pageContext.request.contextPath}/dashboard">Dashboard</a>
            <a href="${pageContext.request.contextPath}/reports" class="active">Reports</a>
        </div>
        <div class="nav-user">
            <span>admin@corp.local</span>
        </div>
    </nav>

    <div class="container">
        <div class="page-header">
            <h1>Asset Reports</h1>
            <p class="subtitle">Summary statistics and breakdowns</p>
        </div>

        <div class="stats-row">
            <div class="stat-card">
                <div class="stat-value">${totalAssets}</div>
                <div class="stat-label">Total Assets</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">$<fmt:formatNumber value="${totalValue}" type="number" minFractionDigits="2"/></div>
                <div class="stat-label">Total Portfolio Value</div>
            </div>
        </div>

        <div class="detail-grid">
            <div class="detail-card">
                <h3>By Category</h3>
                <dl>
                    <c:forEach var="entry" items="${categoryCounts}">
                        <dt>${entry.key}</dt>
                        <dd>${entry.value}</dd>
                    </c:forEach>
                </dl>
            </div>
            <div class="detail-card">
                <h3>By Status</h3>
                <dl>
                    <c:forEach var="entry" items="${statusCounts}">
                        <dt>${entry.key}</dt>
                        <dd>${entry.value}</dd>
                    </c:forEach>
                </dl>
            </div>
        </div>
    </div>

    <footer class="footer">
        <p>&copy; 2024 Corp IT Services - Asset Management Portal v3.2.1</p>
    </footer>
</body>
</html>
