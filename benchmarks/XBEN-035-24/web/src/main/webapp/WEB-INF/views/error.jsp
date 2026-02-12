<%@ page contentType="text/html;charset=UTF-8" language="java" isErrorPage="true" %>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Asset Portal - Error</title>
    <link rel="stylesheet" href="${pageContext.request.contextPath}/css/style.css">
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand">
            <span class="logo">&#9881;</span> Asset Portal
        </div>
        <div class="nav-links">
            <a href="${pageContext.request.contextPath}/dashboard">Dashboard</a>
            <a href="${pageContext.request.contextPath}/reports">Reports</a>
        </div>
        <div class="nav-user">
            <span>admin@corp.local</span>
        </div>
    </nav>
    <div class="container">
        <div class="page-header" style="text-align:center; margin-top: 60px;">
            <h1>Something went wrong</h1>
            <p class="subtitle">The requested resource could not be found or an error occurred.</p>
            <br>
            <a href="${pageContext.request.contextPath}/dashboard" class="btn">Return to Dashboard</a>
        </div>
    </div>
    <footer class="footer">
        <p>&copy; 2024 Corp IT Services - Asset Management Portal v3.2.1</p>
    </footer>
</body>
</html>
