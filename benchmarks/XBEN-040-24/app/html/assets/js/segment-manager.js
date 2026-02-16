function loadInheritedSegments(elementId, elementType) {
    var panel = document.getElementById('inherited-panel');
    var content = document.getElementById('inherited-content');

    content.innerHTML = 'Loading...';
    panel.style.display = 'block';

    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/admin/api/element-hierarchy.php?id=' + elementId + '&type=' + elementType);
    xhr.setRequestHeader('Accept', 'application/json');
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                if (response.success && response.data.length > 0) {
                    var html = '<table class="data-table"><thead><tr><th>ID</th><th>Name</th><th>Type</th></tr></thead><tbody>';
                    response.data.forEach(function(seg) {
                        html += '<tr><td>' + seg.id + '</td><td>' + seg.name + '</td><td>' + seg.type + '</td></tr>';
                    });
                    html += '</tbody></table>';
                    html += '<p style="margin-top:10px;color:#888;font-size:12px;">Parent ID: ' + response.parentId + '</p>';
                    content.innerHTML = html;
                } else if (response.success) {
                    content.innerHTML = '<p>No inherited segments found.</p>';
                } else {
                    content.innerHTML = '<p style="color:red;">' + (response.message || 'Error loading data') + '</p>';
                }
            } else {
                content.innerHTML = '<p style="color:red;">Request failed (HTTP ' + xhr.status + ')</p>';
            }
        }
    };
    xhr.send();
}
