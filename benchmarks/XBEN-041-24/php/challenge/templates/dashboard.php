<?php $pageTitle = 'Dashboard'; $requestUri = '/'; include TEMPLATE_DIR . '/layout_header.php'; ?>
        <h1>Activity Dashboard</h1>
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Products</h3>
                <span class="stat-number"><?= intval($productCount) ?></span>
            </div>
            <div class="stat-card">
                <h3>Categories</h3>
                <span class="stat-number"><?= intval($categoryCount) ?></span>
            </div>
            <div class="stat-card">
                <h3>Media Assets</h3>
                <span class="stat-number"><?= intval($mediaCount) ?></span>
            </div>
        </div>
        <div class="recent-section">
            <h2>Quick Actions</h2>
            <div class="action-grid">
                <a href="/catalog/products/create" class="action-card">Create Product</a>
                <a href="/enrich/media/upload" class="action-card">Upload Media</a>
                <a href="/catalog/categories" class="action-card">Manage Categories</a>
            </div>
        </div>
<?php include TEMPLATE_DIR . '/layout_footer.php'; ?>
