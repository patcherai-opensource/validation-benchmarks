<?php
/**
 * Topic listing - Admin
 *
 * @package   myKnowledgeBase
 */
?>

<div class="admin-header">
    <h1>Topics</h1>
    <div>
        <a class="btn btn-success btn-sm" href="/admin/?action=addtopic">Add New Topic</a>
    </div>
</div>

<?php if (isset($_GET['msg'])): ?>
    <?php if ($_GET['msg'] === 'saved'): ?>
        <div class="alert alert-success">Topic has been saved successfully.</div>
    <?php elseif ($_GET['msg'] === 'updated'): ?>
        <div class="alert alert-success">Topic has been updated successfully.</div>
    <?php elseif ($_GET['msg'] === 'error'): ?>
        <div class="alert alert-danger">An error occurred while processing the topic. <?php echo isset($_GET['detail']) ? htmlspecialchars($_GET['detail']) : ''; ?></div>
    <?php endif; ?>
<?php endif; ?>

<div class="card">
    <table class="table">
        <thead>
            <tr>
                <th>ID</th>
                <th>Image</th>
                <th>Name</th>
                <th>Language</th>
                <th>Description</th>
                <th>Status</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            <?php foreach ($mkb_topics as $id => $topic): ?>
            <tr>
                <td><?php echo $id; ?></td>
                <td>
                    <?php if (!empty($topic['image']) && file_exists(MKB_IMAGES_DIR . $topic['image'])): ?>
                        <img src="/images/<?php echo htmlspecialchars($topic['image']); ?>" style="height:32px;width:32px;object-fit:cover;border-radius:3px;" alt="">
                    <?php else: ?>
                        <span style="color:#ccc;">—</span>
                    <?php endif; ?>
                </td>
                <td><?php echo htmlspecialchars($topic['name']); ?></td>
                <td><?php echo htmlspecialchars($topic['lang']); ?></td>
                <td><?php echo htmlspecialchars(substr($topic['description'], 0, 60)); ?></td>
                <td><?php echo $topic['active'] ? '<span style="color:green">Active</span>' : '<span style="color:red">Inactive</span>'; ?></td>
                <td>
                    <a class="btn btn-info btn-sm" href="/admin/?action=edittopic&id=<?php echo $id; ?>">Edit</a>
                </td>
            </tr>
            <?php endforeach; ?>
        </tbody>
    </table>
</div>
