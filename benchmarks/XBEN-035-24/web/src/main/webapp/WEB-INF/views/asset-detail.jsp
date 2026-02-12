<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<%@ taglib prefix="fmt" uri="http://java.sun.com/jsp/jstl/fmt" %>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Asset Portal - ${asset.name}</title>
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
        <div class="page-header">
            <a href="${pageContext.request.contextPath}/dashboard" class="back-link">&larr; Back to Dashboard</a>
            <h1>${asset.name}</h1>
            <p class="subtitle">Asset #${asset.id} &mdash; ${asset.serialNumber}</p>
        </div>

        <div class="detail-grid">
            <div class="detail-card">
                <h3>General Information</h3>
                <dl>
                    <dt>Name</dt>
                    <dd id="field-name">${asset.name}</dd>
                    <dt>Serial Number</dt>
                    <dd id="field-serialNumber">${asset.serialNumber}</dd>
                    <dt>Category</dt>
                    <dd id="field-category">${asset.category.displayName}</dd>
                    <dt>Status</dt>
                    <dd id="field-status">${asset.status.label}</dd>
                </dl>
            </div>

            <div class="detail-card">
                <h3>Location</h3>
                <dl>
                    <dt>Building</dt>
                    <dd>${asset.location.building}</dd>
                    <dt>Floor</dt>
                    <dd>${asset.location.floor}</dd>
                    <dt>Room</dt>
                    <dd>${asset.location.room}</dd>
                </dl>
            </div>

            <div class="detail-card">
                <h3>Assignment</h3>
                <dl>
                    <dt>Assigned To</dt>
                    <dd>${asset.assignedTo}</dd>
                    <dt>Purchase Date</dt>
                    <dd><fmt:formatDate value="${asset.purchaseDate}" pattern="yyyy-MM-dd"/></dd>
                    <dt>Purchase Price</dt>
                    <dd>$<fmt:formatNumber value="${asset.purchasePrice}" type="number" minFractionDigits="2"/></dd>
                </dl>
            </div>

            <div class="detail-card">
                <h3>Notes</h3>
                <p>${asset.notes}</p>
            </div>
        </div>

        <div class="detail-card" style="margin-top: 20px;">
            <h3>Quick Property Lookup</h3>
            <p class="help-text">Retrieve specific property values for this asset using dot notation (e.g., <code>name</code>, <code>location.building</code>, <code>category.displayName</code>).</p>
            <div class="property-lookup">
                <input type="text" id="propertyField" placeholder="Enter property path..." class="input-field">
                <button onclick="lookupProperty()" class="btn">Lookup</button>
            </div>
            <div id="propertyResult" class="result-box" style="display:none;"></div>
        </div>
    </div>

    <footer class="footer">
        <p>&copy; 2024 Corp IT Services - Asset Management Portal v3.2.1</p>
    </footer>

    <script>
        function lookupProperty() {
            var field = document.getElementById('propertyField').value;
            var assetId = ${asset.id};
            var resultBox = document.getElementById('propertyResult');

            if (!field) {
                resultBox.style.display = 'block';
                resultBox.className = 'result-box error';
                resultBox.textContent = 'Please enter a property path.';
                return;
            }

            fetch('${pageContext.request.contextPath}/api/asset/property?id=' + assetId + '&field=' + encodeURIComponent(field))
                .then(function(response) { return response.json(); })
                .then(function(data) {
                    resultBox.style.display = 'block';
                    if (data.error) {
                        resultBox.className = 'result-box error';
                        resultBox.textContent = data.error;
                    } else {
                        resultBox.className = 'result-box success';
                        resultBox.textContent = data.field + ' = ' + data.value;
                    }
                })
                .catch(function(err) {
                    resultBox.style.display = 'block';
                    resultBox.className = 'result-box error';
                    resultBox.textContent = 'Request failed.';
                });
        }
    </script>
</body>
</html>
