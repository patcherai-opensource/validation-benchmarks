<?php
/**
 * Add new topic form
 *
 * @package   myKnowledgeBase
 */

$csrf_token = mkb_generate_token('save-topic');
?>

<div class="admin-header">
    <h1>Add New Topic</h1>
    <div>
        <a class="btn btn-info btn-sm" href="/admin/?action=topics">Back to Topics</a>
    </div>
</div>

<div class="card">
    <form enctype="multipart/form-data" action="/admin/?action=savetopic" method="post">
        <input type="hidden" name="csrf" value="<?php echo htmlspecialchars($csrf_token); ?>">

        <div class="form-group">
            <label for="name">Topic Name</label>
            <input type="text" id="name" name="name" class="form-control" required>
        </div>

        <div class="form-group">
            <label for="description">Description</label>
            <textarea id="description" name="description" class="form-control" rows="3"></textarea>
        </div>

        <div class="form-group">
            <label for="lang">Language</label>
            <select id="lang" name="lang" class="form-control">
                <?php foreach ($mkb_languages as $code => $label): ?>
                    <option value="<?php echo htmlspecialchars($code); ?>" <?php echo $code === 'en' ? 'selected' : ''; ?>>
                        <?php echo htmlspecialchars($label); ?> (<?php echo htmlspecialchars($code); ?>)
                    </option>
                <?php endforeach; ?>
            </select>
        </div>

        <div class="form-group">
            <label for="parent_id">Parent Topic</label>
            <select id="parent_id" name="parent_id" class="form-control">
                <option value="0">— None (Top Level) —</option>
                <?php foreach ($mkb_topics as $id => $topic): ?>
                    <?php if ($topic['parent_id'] === 0): ?>
                        <option value="<?php echo $id; ?>"><?php echo htmlspecialchars($topic['name']); ?></option>
                    <?php endif; ?>
                <?php endforeach; ?>
            </select>
        </div>

        <div class="form-group">
            <label for="image">Topic Image</label>
            <input type="file" id="image" name="image" class="form-control" accept="image/*">
            <small style="color:#7f8c8d;">Allowed: JPEG, PNG, GIF, WebP. Max size: 2MB</small>
        </div>

        <div class="form-group">
            <label>
                <input type="checkbox" name="active" value="1" checked> Active
            </label>
        </div>

        <button type="submit" class="btn btn-primary">Save Topic</button>
    </form>
</div>
