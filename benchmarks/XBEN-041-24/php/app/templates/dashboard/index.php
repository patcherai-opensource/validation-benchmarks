<?php $pageTitle = 'Dashboard - Akeneo PIM'; $currentPage = 'dashboard'; ?>
<?php include __DIR__ . '/../layout/header.php'; ?>

<div class="page-header">
    <h1>Dashboard</h1>
</div>

<div class="stat-cards">
    <div class="stat-card">
        <div class="number">5</div>
        <div class="label">Products</div>
    </div>
    <div class="stat-card">
        <div class="number">5</div>
        <div class="label">Categories</div>
    </div>
    <div class="stat-card">
        <div class="number">3</div>
        <div class="label">Channels</div>
    </div>
    <div class="stat-card">
        <div class="number">77%</div>
        <div class="label">Avg. Completeness</div>
    </div>
</div>

<div class="card">
    <h3 style="margin-bottom: 16px; font-weight: 400;">Recent Activity</h3>
    <table>
        <thead>
            <tr>
                <th>Action</th>
                <th>Product</th>
                <th>User</th>
                <th>Date</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Updated</td>
                <td>1080p Monitor (AKN-001)</td>
                <td>Julia Stark</td>
                <td>2024-03-15 14:23</td>
            </tr>
            <tr>
                <td>Created</td>
                <td>4K Webcam (AKN-005)</td>
                <td>John Doe</td>
                <td>2024-02-20 09:45</td>
            </tr>
            <tr>
                <td>Media uploaded</td>
                <td>Wireless Mouse (AKN-004)</td>
                <td>Mary Smith</td>
                <td>2024-02-18 11:12</td>
            </tr>
            <tr>
                <td>Updated</td>
                <td>Ergonomic Keyboard (AKN-002)</td>
                <td>Julia Stark</td>
                <td>2024-02-15 16:30</td>
            </tr>
        </tbody>
    </table>
</div>

<?php include __DIR__ . '/../layout/footer.php'; ?>