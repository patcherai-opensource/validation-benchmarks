<?php
$page_title = 'Dashboard';
include(__DIR__ . "/layout_header.php");

$total_articles = 0;
$active_articles = 0;
$total_categories = 0;
$total_visits = 0;

$r = mysqli_query($db_connect, "SELECT COUNT(*) as cnt FROM kb_articledata");
if ($r && $row = mysqli_fetch_assoc($r)) $total_articles = $row['cnt'];

$r = mysqli_query($db_connect, "SELECT COUNT(*) as cnt FROM kb_articledata WHERE active='yes'");
if ($r && $row = mysqli_fetch_assoc($r)) $active_articles = $row['cnt'];

$r = mysqli_query($db_connect, "SELECT COUNT(*) as cnt FROM kb_categories");
if ($r && $row = mysqli_fetch_assoc($r)) $total_categories = $row['cnt'];

$r = mysqli_query($db_connect, "SELECT SUM(visits) as total FROM kb_visits");
if ($r && $row = mysqli_fetch_assoc($r)) $total_visits = $row['total'] ?? 0;
?>

<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2"><i class="fas fa-tachometer-alt"></i> Dashboard</h1>
</div>

<div class="row mb-4">
    <div class="col-xl-3 col-md-6">
        <div class="card bg-primary text-white mb-3">
            <div class="card-body">
                <div class="d-flex justify-content-between">
                    <div>
                        <div class="text-white-50 small">Total Articles</div>
                        <div class="fs-4 fw-bold"><?= $total_articles ?></div>
                    </div>
                    <i class="fas fa-file-alt fa-2x opacity-50"></i>
                </div>
            </div>
        </div>
    </div>
    <div class="col-xl-3 col-md-6">
        <div class="card bg-success text-white mb-3">
            <div class="card-body">
                <div class="d-flex justify-content-between">
                    <div>
                        <div class="text-white-50 small">Published</div>
                        <div class="fs-4 fw-bold"><?= $active_articles ?></div>
                    </div>
                    <i class="fas fa-check-circle fa-2x opacity-50"></i>
                </div>
            </div>
        </div>
    </div>
    <div class="col-xl-3 col-md-6">
        <div class="card bg-info text-white mb-3">
            <div class="card-body">
                <div class="d-flex justify-content-between">
                    <div>
                        <div class="text-white-50 small">Categories</div>
                        <div class="fs-4 fw-bold"><?= $total_categories ?></div>
                    </div>
                    <i class="fas fa-folder fa-2x opacity-50"></i>
                </div>
            </div>
        </div>
    </div>
    <div class="col-xl-3 col-md-6">
        <div class="card bg-warning text-white mb-3">
            <div class="card-body">
                <div class="d-flex justify-content-between">
                    <div>
                        <div class="text-white-50 small">Total Visits</div>
                        <div class="fs-4 fw-bold"><?= number_format($total_visits) ?></div>
                    </div>
                    <i class="fas fa-eye fa-2x opacity-50"></i>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="card shadow-sm">
    <div class="card-header">
        <h5 class="mb-0"><i class="fas fa-clock"></i> Recent Articles</h5>
    </div>
    <div class="card-body">
        <table class="table table-hover">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Title</th>
                    <th>Author</th>
                    <th>Status</th>
                    <th>Updated</th>
                </tr>
            </thead>
            <tbody>
                <?php
                $r = mysqli_query($db_connect, "SELECT id, title, author, active, created FROM kb_articledata ORDER BY created DESC LIMIT 10");
                while ($r && $row = mysqli_fetch_assoc($r)):
                ?>
                <tr>
                    <td><?= intval($row['id']) ?></td>
                    <td><a href="index.php?action=editarticle&id=<?= intval($row['id']) ?>"><?= htmlspecialchars($row['title']) ?></a></td>
                    <td><?= htmlspecialchars($row['author']) ?></td>
                    <td>
                        <?php if ($row['active'] === 'yes'): ?>
                            <span class="badge bg-success">Published</span>
                        <?php else: ?>
                            <span class="badge bg-secondary">Draft</span>
                        <?php endif; ?>
                    </td>
                    <td><?= htmlspecialchars($row['created']) ?></td>
                </tr>
                <?php endwhile; ?>
            </tbody>
        </table>
    </div>
</div>

<?php include(__DIR__ . "/layout_footer.php"); ?>
