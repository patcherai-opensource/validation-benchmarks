<div class="col-md-4">
    <!-- Quick Actions Widget -->
    <div class="card my-4 border-primary">
        <h5 class="card-header bg-primary text-white">Quick Actions</h5>
        <div class="card-body">
            <div class="d-grid gap-2">
                <a href="/upload.php" class="btn btn-outline-primary">Upload Files</a>
                <a href="/files/" class="btn btn-outline-secondary">Browse Files</a>
            </div>
        </div>
    </div>

    <!-- File Types Widget -->
    <div class="card my-4">
        <h5 class="card-header">Supported File Types</h5>
        <div class="card-body">
            <div class="row">
                <div class="col-lg-6">
                    <ul class="list-unstyled mb-0">
                        <li><i class="bi bi-file-earmark-pdf"></i> PDF</li>
                        <li><i class="bi bi-file-earmark-word"></i> DOC/DOCX</li>
                        <li><i class="bi bi-file-earmark-excel"></i> XLS/XLSX</li>
                    </ul>
                </div>
                <div class="col-lg-6">
                    <ul class="list-unstyled mb-0">
                        <li><i class="bi bi-file-earmark-image"></i> Images</li>
                        <li><i class="bi bi-file-earmark-text"></i> TXT</li>
                        <li><i class="bi bi-file-earmark-zip"></i> Archives</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <!-- System Status -->
    <div class="card my-4">
        <h5 class="card-header">System Status</h5>
        <div class="card-body">
            <h6>Active Users: <span id="userCount">0</span></h6>
            <p>Storage Used:</p>
            <div class="progress">
                <div class="progress-bar bg-success" role="progressbar" style="width: 35%" aria-valuenow="35" aria-valuemin="0" aria-valuemax="100">35%</div>
            </div>
            <small class="text-muted">350 GB / 1 TB</small>
        </div>
    </div>

    <!-- Recent Activity -->
    <div class="card my-4">
        <h5 class="card-header">Recent Activity</h5>
        <div class="card-body">
            <ul class="list-unstyled mb-0" id="activityList">
            </ul>
        </div>
    </div>
</div>

<script type="text/javascript">
    document.addEventListener('DOMContentLoaded', function() {
        const activities = [
            "report_q4.pdf uploaded",
            "budget_2024.xlsx modified",
            "team_photo.jpg uploaded",
            "meeting_notes.docx created",
            "backup.zip downloaded"
        ];
        
        function updateStatus() {
            const userCount = Math.floor(Math.random() * 50) + 10;
            document.getElementById('userCount').innerText = userCount;
            
            const ul = document.getElementById('activityList');
            ul.innerHTML = "";
            const shuffled = activities.sort(() => 0.5 - Math.random());
            shuffled.slice(0, 3).forEach(activity => {
                const li = document.createElement('li');
                li.innerHTML = '<small class="text-muted">' + activity + '</small>';
                ul.appendChild(li);
            });
        }
        updateStatus();
        setInterval(updateStatus, 8000);
    });
</script>
