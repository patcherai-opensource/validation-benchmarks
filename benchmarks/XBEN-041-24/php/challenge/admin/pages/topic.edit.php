<?php
/**
 * Edit topic form
 *
 * @package   myKnowledgeBase
 */

$topicId = isset($_GET['id']) ? (int)$_GET['id'] : 0;

if (!isset($mkb_topics[$topicId])) {
    header('Location: /admin/?action=topics&msg=error&detail=Topic+not+found');
    exit();
}

$topic = $mkb_topics[$topicId];
$csrf_token = mkb_generate_token('update-topic');
?>

<div class="admin-header">
    <h1>Edit Topic: <?php echo htmlspecialchars($topic['name']); ?></h1>
    <div>
        <a class="btn btn-info btn-sm" href="/admin/?action=topics">Back to Topics</a>
    </div>
</div>

<div class="card">
    <form enctype="multipart/form-data" action="/admin/?action=updatetopic" method="post">
        <input type="hidden" name="csrf" value="<?php echo htmlspecialchars($csrf_token); ?>">
        <input type="hidden" name="topic_id" value="<?php echo $topicId; ?>">

        <div class="form-group">
            <label for="name">Topic Name</label>
            <input type="text" id="name" name="name" class="form-control" value="<?php echo htmlspecialchars($topic['name']); ?>" required>
        </div>

        <div class="form-group">
            <label for="description">Description</label>
            <textarea id="description" name="description" class="form-control" rows="3"><?php echo htmlspecialchars($topic['description']); ?></textarea>
        </div>

        <div class="form-group">
            <label for="lang">Language</label>
            <select id="lang" name="lang" class="form-control">
                <?php foreach ($mkb_languages as $code => $label): ?>
                    <option value="<?php echo htmlspecialchars($code); ?>" <?php echo $code === $topic['lang'] ? 'selected' : ''; ?>>
                        <?php echo htmlspecialchars($label); ?> (<?php echo htmlspecialchars($code); ?>)
                    </option>
                <?php endforeach; ?>
            </select>
        </div>

        <div class="form-group">
            <label for="parent_id">Parent Topic</label>
            <select id="parent_id" name="parent_id" class="form-control">
                <option value="0">— None (Top Level) —</option>
                <?php foreach ($mkb_topics as $id => $t): ?>
                    <?php if ($t['parent_id'] === 0 && $id !== $topicId): ?>
                        <option value="<?php echo $id; ?>" <?php echo $id === $topic['parent_id'] ? 'selected' : ''; ?>>
                            <?php echo htmlspecialchars($t['name']); ?>
                        </option>
                    <?php endif; ?>
                <?php endforeach; ?>
            </select>
        </div>

        <div class="form-group">
            <label for="image">Topic Image</label>
            <?php if (!empty($topic['image']) && file_exists(MKB_IMAGES_DIR . $topic['image'])): ?>
                <div style="margin-bottom:10px;">
                    <img src="/images/<?php echo htmlspecialchars($topic['image']); ?>" style="max-height:100px;border-radius:4px;" alt="">
                    <br><small>Current: <?php echo htmlspecialchars($topic['image']); ?></small>
                </div>
            <?php endif; ?>
            <input type="file" id="image" name="image" class="form-control" accept="image/*">
            <small style="color:#7f8c8d;">Leave empty to keep current image. Allowed: JPEG, PNG, GIF, WebP. Max size: 2MB</small>
        </div>

        <div class="form-group">
            <label>
                <input type="checkbox" name="active" value="1" <?php echo $topic['active'] ? 'checked' : ''; ?>> Active
            </label>
        </div>

        <button type="submit" class="btn btn-primary">Update Topic</button>
    </form>
</div>
