<div class="col-md-3">
    <!-- Quick Links Widget -->
    <div class="card my-4">
        <h5 class="card-header">Quick Access</h5>
        <div class="card-body">
            <ul class="list-unstyled mb-0">
                <li><a href="/index.php">Course Catalog</a></li>
                <li><a href="/database.php">Database Fields</a></li>
                <li><a href="/modules.php">All Modules</a></li>
                <li><a href="/about.php">About LMS</a></li>
            </ul>
        </div>
    </div>

    <!-- Categories Widget -->
    <div class="card my-4">
        <h5 class="card-header">Course Categories</h5>
        <div class="card-body">
            <ul class="list-unstyled mb-0 small">
                <li><a href="#">Computer Science</a></li>
                <li><a href="#">Data Science</a></li>
                <li><a href="#">Security</a></li>
                <li><a href="#">Development</a></li>
                <li><a href="#">Cloud Computing</a></li>
                <li><a href="#">IT Operations</a></li>
            </ul>
        </div>
    </div>

    <!-- Side Widget -->
    <div class="card my-4">
        <h5 class="card-header">Platform Stats</h5>
        <div class="card-body">
            <ul class="list-unstyled mb-0 small">
                <li><strong>Active Users:</strong> <span id="userCount">0</span></li>
                <li><strong>Total Courses:</strong> 8</li>
                <li><strong>Modules:</strong> 6</li>
            </ul>
        </div>
    </div>
</div>

<script type="text/javascript">
    document.addEventListener('DOMContentLoaded', function() {
        function updateStats() {
            const userCount = Math.floor(Math.random() * 150) + 50;
            document.getElementById('userCount').innerText = userCount;
        }
        updateStats();
        setInterval(updateStats, 8000);
    });
</script>
