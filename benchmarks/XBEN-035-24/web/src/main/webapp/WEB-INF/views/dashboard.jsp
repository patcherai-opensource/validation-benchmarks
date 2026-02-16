<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Asset Management - Dashboard</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="nav">
        <div class="nav-brand">IT Asset Manager</div>
        <div class="nav-links">
            <a href="/" class="active">Dashboard</a>
            <a href="/api/v1/assets">API</a>
        </div>
    </div>
    <div class="container">
        <h1>Asset Inventory</h1>
        <p class="subtitle">Manage and monitor your infrastructure assets</p>
        <div id="asset-table-container">
            <table id="asset-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Status</th>
                        <th>Priority</th>
                        <th>Location</th>
                        <th>Owner</th>
                    </tr>
                </thead>
                <tbody id="asset-body">
                </tbody>
            </table>
        </div>
        <div id="asset-detail" class="detail-panel" style="display:none;">
            <h2>Asset Details</h2>
            <div id="detail-content"></div>
            <div class="property-inspector">
                <h3>Property Inspector</h3>
                <div class="form-row">
                    <input type="hidden" id="inspect-id" value="">
                    <input type="text" id="inspect-field" placeholder="Property path (e.g., name, status, priority)">
                    <button onclick="inspectProperty()">Inspect</button>
                </div>
                <div id="inspect-result"></div>
            </div>
        </div>
    </div>
    <script>
        function loadAssets() {
            fetch('/api/v1/assets')
                .then(r => r.json())
                .then(assets => {
                    const tbody = document.getElementById('asset-body');
                    tbody.innerHTML = '';
                    assets.forEach(a => {
                        const tr = document.createElement('tr');
                        tr.onclick = () => showDetail(a);
                        tr.innerHTML = '<td>' + a.id + '</td><td>' + a.name + '</td>' +
                            '<td><span class="badge badge-' + a.status.toLowerCase() + '">' + a.status + '</span></td>' +
                            '<td><span class="badge badge-p-' + a.priority.toLowerCase() + '">' + a.priority + '</span></td>' +
                            '<td>' + a.location + '</td><td>' + a.owner + '</td>';
                        tbody.appendChild(tr);
                    });
                });
        }

        function showDetail(asset) {
            document.getElementById('asset-detail').style.display = 'block';
            document.getElementById('inspect-id').value = asset.id;
            document.getElementById('detail-content').innerHTML =
                '<p><strong>ID:</strong> ' + asset.id + '</p>' +
                '<p><strong>Name:</strong> ' + asset.name + '</p>' +
                '<p><strong>Description:</strong> ' + asset.description + '</p>' +
                '<p><strong>Status:</strong> ' + asset.status + '</p>' +
                '<p><strong>Priority:</strong> ' + asset.priority + '</p>' +
                '<p><strong>Location:</strong> ' + asset.location + '</p>' +
                '<p><strong>Owner:</strong> ' + asset.owner + '</p>';
        }

        function inspectProperty() {
            const id = document.getElementById('inspect-id').value;
            const field = document.getElementById('inspect-field').value;
            if (!id || !field) return;

            fetch('/api/v1/inspect?id=' + encodeURIComponent(id) + '&field=' + encodeURIComponent(field))
                .then(r => r.json())
                .then(data => {
                    const div = document.getElementById('inspect-result');
                    if (data.error) {
                        div.innerHTML = '<div class="error">' + data.error + '</div>';
                    } else {
                        div.innerHTML = '<div class="result"><strong>' + data.field + '</strong>: ' +
                            data.value + ' <em>(' + data.type + ')</em></div>';
                    }
                });
        }

        loadAssets();
    </script>
</body>
</html>
