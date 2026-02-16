<?php
$page_title = 'Categories';
include(__DIR__ . "/layout_header.php");
?>

<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2"><i class="fas fa-folder"></i> Categories</h1>
</div>

<div class="card shadow-sm">
    <div class="card-body">
        <table class="table table-striped">
            <thead class="table-dark">
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Description</th>
                    <th>Articles</th>
                    <th>Language</th>
                </tr>
            </thead>
            <tbody>
                <?php
                $query = "SELECT c.category_id, c.name, c.description, c.lang,
                          COUNT(ac.article_id) as article_count
                          FROM kb_categories c
                          LEFT JOIN kb_article_categories ac ON c.category_id = ac.category_id
                          GROUP BY c.category_id
                          ORDER BY c.display_order";
                $r = mysqli_query($db_connect, $query);
                while ($r && $row = mysqli_fetch_assoc($r)):
                ?>
                <tr>
                    <td><?= intval($row['category_id']) ?></td>
                    <td><strong><?= htmlspecialchars($row['name']) ?></strong></td>
                    <td><?= htmlspecialchars($row['description'] ?? '') ?></td>
                    <td><span class="badge bg-primary"><?= intval($row['article_count']) ?></span></td>
                    <td><?= htmlspecialchars($row['lang']) ?></td>
                </tr>
                <?php endwhile; ?>
            </tbody>
        </table>
    </div>
</div>

<?php include(__DIR__ . "/layout_footer.php"); ?>
