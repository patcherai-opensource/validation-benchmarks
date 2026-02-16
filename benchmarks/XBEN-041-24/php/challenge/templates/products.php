<?php $pageTitle = 'Products'; $requestUri = '/catalog/products'; include TEMPLATE_DIR . '/layout_header.php'; ?>
        <div class="page-header">
            <h1>Products</h1>
            <a href="/catalog/products/create" class="btn btn-primary">Create</a>
        </div>
        <table class="data-table">
            <thead>
                <tr>
                    <th>SKU</th>
                    <th>Name</th>
                    <th>Category</th>
                    <th>Price</th>
                    <th>Updated</th>
                </tr>
            </thead>
            <tbody>
                <?php if (empty($products)): ?>
                    <tr><td colspan="5" class="empty-state">No products found</td></tr>
                <?php else: ?>
                    <?php foreach ($products as $product): ?>
                        <tr>
                            <td><?= htmlspecialchars($product['sku'], ENT_QUOTES, 'UTF-8') ?></td>
                            <td><?= htmlspecialchars($product['name'], ENT_QUOTES, 'UTF-8') ?></td>
                            <td><?= htmlspecialchars($product['category_name'] ?? '-', ENT_QUOTES, 'UTF-8') ?></td>
                            <td><?= number_format($product['price'], 2) ?></td>
                            <td><?= htmlspecialchars($product['updated_at'], ENT_QUOTES, 'UTF-8') ?></td>
                        </tr>
                    <?php endforeach; ?>
                <?php endif; ?>
            </tbody>
        </table>
        <?php if ($total > $perPage): ?>
            <div class="pagination">
                <?php for ($i = 1; $i <= ceil($total / $perPage); $i++): ?>
                    <a href="/catalog/products?page=<?= $i ?>" class="<?= $i === $page ? 'active' : '' ?>"><?= $i ?></a>
                <?php endfor; ?>
            </div>
        <?php endif; ?>
<?php include TEMPLATE_DIR . '/layout_footer.php'; ?>
