<?php $pageTitle = 'Create Product'; $requestUri = '/catalog/products'; include TEMPLATE_DIR . '/layout_header.php'; ?>
        <h1>Create Product</h1>
        <form method="post" class="form-standard">
            <div class="form-group">
                <label for="sku">SKU</label>
                <input type="text" id="sku" name="sku" required>
            </div>
            <div class="form-group">
                <label for="name">Name</label>
                <input type="text" id="name" name="name" required>
            </div>
            <div class="form-group">
                <label for="description">Description</label>
                <textarea id="description" name="description" rows="4"></textarea>
            </div>
            <div class="form-group">
                <label for="category_id">Category</label>
                <select id="category_id" name="category_id">
                    <option value="0">-- No Category --</option>
                    <?php foreach ($categories as $cat): ?>
                        <option value="<?= $cat['id'] ?>"><?= htmlspecialchars($cat['name'], ENT_QUOTES, 'UTF-8') ?></option>
                    <?php endforeach; ?>
                </select>
            </div>
            <div class="form-group">
                <label for="price">Price</label>
                <input type="number" id="price" name="price" step="0.01" min="0">
            </div>
            <div class="form-actions">
                <a href="/catalog/products" class="btn btn-secondary">Cancel</a>
                <button type="submit" class="btn btn-primary">Save</button>
            </div>
        </form>
<?php include TEMPLATE_DIR . '/layout_footer.php'; ?>
