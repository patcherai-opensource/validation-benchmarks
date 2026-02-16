<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>KBPortal Admin - <?= htmlspecialchars($page_title ?? 'Dashboard') ?></title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    <style>
        .sidebar { min-height: calc(100vh - 56px); background-color: #343a40; }
        .sidebar .nav-link { color: rgba(255,255,255,.75); padding: .75rem 1rem; }
        .sidebar .nav-link:hover { color: #fff; background-color: rgba(255,255,255,.1); }
        .sidebar .nav-link.active { color: #fff; background-color: rgba(255,255,255,.15); }
        .sidebar .nav-link i { width: 20px; margin-right: 8px; }
        .main-content { padding: 20px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="index.php"><i class="fas fa-book-open"></i> KBPortal Admin</a>
            <div class="navbar-nav ms-auto">
                <span class="nav-link text-light"><i class="fas fa-user"></i> <?= htmlspecialchars($current_display_name) ?> (<?= htmlspecialchars($current_permission) ?>)</span>
                <a class="nav-link" href="../index.php?action=logout"><i class="fas fa-sign-out-alt"></i> Logout</a>
            </div>
        </div>
    </nav>
    <div class="container-fluid">
        <div class="row">
            <nav class="col-md-2 sidebar p-0">
                <ul class="nav flex-column pt-3">
                    <li class="nav-item">
                        <a class="nav-link <?= ($action ?? '') == 'dashboard' ? 'active' : '' ?>" href="index.php">
                            <i class="fas fa-tachometer-alt"></i> Dashboard
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link <?= in_array($action ?? '', ['listarticles','editarticle','newarticle']) ? 'active' : '' ?>" href="index.php?action=listarticles">
                            <i class="fas fa-file-alt"></i> Articles
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link <?= ($action ?? '') == 'categories' ? 'active' : '' ?>" href="index.php?action=categories">
                            <i class="fas fa-folder"></i> Categories
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="index.php?action=newarticle">
                            <i class="fas fa-plus-circle"></i> New Article
                        </a>
                    </li>
                </ul>
            </nav>
            <main class="col-md-10 main-content">
