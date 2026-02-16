<?php
$page_title = 'All Articles';
include(__DIR__ . "/layout_header.php");
?>

<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2"><i class="fas fa-file-alt"></i> Articles</h1>
    <a href="index.php?action=newarticle" class="btn btn-primary"><i class="fas fa-plus"></i> Add New Article</a>
</div>

<div class="card shadow-sm">
    <div class="card-body">
        <table class="table table-striped table-hover">
            <thead class="table-dark">
                <tr>
                    <th>ID</th>
                    <th>Solution ID</th>
                    <th>Title</th>
                    <th>Category</th>
                    <th>Author</th>
                    <th>Status</th>
                    <th>Visits</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                <?php
                $query = "SELECT a.id, a.solution_id, a.title, a.author, a.active, a.email,
                          COALESCE(c.name, 'Uncategorized') as category_name,
                          COALESCE(v.visits, 0) as visit_count
                          FROM kb_articledata a
                          LEFT JOIN kb_article_categories ac ON a.id = ac.article_id
                          LEFT JOIN kb_categories c ON ac.category_id = c.category_id
                          LEFT JOIN kb_visits v ON a.id = v.id AND a.lang = v.lang
                          ORDER BY a.id DESC";
                $r = mysqli_query($db_connect, $query);
                while ($r && $row = mysqli_fetch_assoc($r)):
                ?>
                <tr>
                    <td><?= intval($row['id']) ?></td>
                    <td>#<?= intval($row['solution_id']) ?></td>
                    <td><a href="index.php?action=editarticle&id=<?= intval($row['id']) ?>"><?= htmlspecialchars($row['title']) ?></a></td>
                    <td><span class="badge bg-info"><?= htmlspecialchars($row['category_name']) ?></span></td>
                    <td><?= htmlspecialchars($row['author']) ?></td>
                    <td>
                        <?php if ($row['active'] === 'yes'): ?>
                            <span class="badge bg-success">Published</span>
                        <?php else: ?>
                            <span class="badge bg-secondary">Draft</span>
                        <?php endif; ?>
                    </td>
                    <td><?= intval($row['visit_count']) ?></td>
                    <td>
                        <a href="index.php?action=editarticle&id=<?= intval($row['id']) ?>" class="btn btn-sm btn-outline-primary" title="Edit">
                            <i class="fas fa-edit"></i>
                        </a>
                    </td>
                </tr>
                <?php endwhile; ?>
            </tbody>
        </table>
    </div>
</div>

<?php include(__DIR__ . "/layout_footer.php"); ?>
