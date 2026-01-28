<div class="col-md-4">
    <!-- Search Widget -->
    <div class="card my-4">
        <h5 class="card-header">Content Search</h5>
        <div class="card-body">
            <div class="input-group">
                <input type="text" class="form-control" placeholder="Search content...">
                <span class="input-group-append">
                    <button class="btn btn-secondary" type="button">Search</button>
                </span>
            </div>
        </div>
    </div>

    <!-- Content Types Widget -->
    <div class="card my-4">
        <h5 class="card-header">Content Types</h5>
        <div class="card-body">
            <div class="row">
                <div class="col-lg-6">
                    <ul class="list-unstyled mb-0">
                        <li><a href="#">Articles</a></li>
                        <li><a href="#">Blog Posts</a></li>
                        <li><a href="#">Landing Pages</a></li>
                    </ul>
                </div>
                <div class="col-lg-6">
                    <ul class="list-unstyled mb-0">
                        <li><a href="#">Media Files</a></li>
                        <li><a href="#">Documents</a></li>
                        <li><a href="#">Images</a></li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <!-- System Info Widget -->
    <div class="card my-4">
        <h5 class="card-header">Platform Status</h5>
        <div class="card-body">
            <h6>Active Sessions: <span id="visitorCount">0</span></h6>
            <p>Connected Nodes:</p>
            <ul id="visitorCountries">
            </ul>
        </div>
    </div>

    <div class="card my-4">
        <h5 class="card-header">Quick Actions</h5>
        <div class="card-body">
            <h6>Content Management</h6>
            <ul class="list-unstyled">
                <li><a href="/posts/upload-article.php">Upload Media</a></li>
                <li><a href="/api/content/list">Content API</a></li>
                <li><a href="/admin/dashboard.php">Dashboard</a></li>
            </ul>
        </div>
    </div>
</div>

<script type="text/javascript">
    document.addEventListener('DOMContentLoaded', function() {
        const countries = ["Argentina", "Poland", "USA", "Canada", "Brazil", "India", "Germany", "France", "Australia", "Japan", "South Korea", "South Africa"];
        
        function updateVisitors() {
            const visitorCount = Math.floor(Math.random() * 500) + 100;
            document.getElementById('visitorCount').innerText = visitorCount;
            const selectedCountries = [];
            for (let i = 0; i < 3; i++) {
                const index = Math.floor(Math.random() * countries.length);
                if (!selectedCountries.includes(countries[index])) {
                    selectedCountries.push(countries[index]);
                }
            }
            const ul = document.getElementById('visitorCountries');
            ul.innerHTML = "";
            selectedCountries.forEach(country => {
                const li = document.createElement('li');
                li.innerText = country;
                ul.appendChild(li);
            });
        }
        updateVisitors();
        setInterval(updateVisitors, 5000);
    });
</script>
