<?php
// EduLearn LMS - Course Catalog
$json_data = file_get_contents('courses.json');
$courses = json_decode($json_data, true);

// Define how many courses per page
$limit = 6;

// Get the current page number
$page = isset($_GET['page']) ? (int)$_GET['page'] : 1;
$total_courses = count($courses);
$total_pages = ceil($total_courses / $limit);
$start = ($page - 1) * $limit;

// Slice the courses array to get the courses for the current page
$display_courses = array_slice($courses, $start, $limit);
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>EduLearn LMS - Online Learning Platform</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .course-card { transition: transform 0.2s; }
        .course-card:hover { transform: translateY(-5px); }
        .badge-field { font-size: 0.75rem; }
    </style>
</head>
<body>
    <!-- Navigation Bar -->
    <? include("include/navigation-bar.php") ?>

    <!-- Header -->
    <header class="py-5 bg-primary text-white mb-4">
        <div class="container">
            <div class="text-center my-4">
                <h1 class="fw-bolder">EduLearn LMS</h1>
                <p class="lead mb-0">Empowering Education Through Technology</p>
                <small class="text-light">Version 4.3.2</small>
            </div>
        </div>
    </header>

    <!-- Main Content Section -->
    <div class="container">
        <div class="row mb-4">
            <div class="col-12">
                <div class="alert alert-info">
                    <strong>Welcome!</strong> Browse our course catalog or access the <a href="database.php">Database Module</a> to manage course data fields.
                </div>
            </div>
        </div>
        
        <div class="row">
            <!-- Course Cards Column -->
            <div class="col-md-9">
                <h3 class="mb-4">Available Courses</h3>
                <div class="row">
                    <?php foreach ($display_courses as $course): ?>
                        <div class="col-md-6 mb-4">
                            <div class="card course-card h-100">
                                <img class="card-img-top" src="<?= htmlspecialchars($course['image_url']); ?>" style="height: 150px; object-fit: cover;" alt="<?= htmlspecialchars($course['title']); ?>">
                                <div class="card-body">
                                    <h5 class="card-title"><?= htmlspecialchars($course['title']); ?></h5>
                                    <p class="card-text small"><?= htmlspecialchars($course['description']); ?></p>
                                    <span class="badge bg-secondary badge-field"><?= htmlspecialchars($course['category']); ?></span>
                                </div>
                                <div class="card-footer">
                                    <a href="course.php?id=<?= htmlspecialchars($course['id']); ?>" class="btn btn-sm btn-primary">View Course</a>
                                </div>
                            </div>
                        </div>
                    <?php endforeach; ?>
                </div>

                <!-- Pagination -->
                <ul class="pagination justify-content-center mb-4">
                    <?php for ($i = 1; $i <= $total_pages; $i++): ?>
                        <li class="page-item <?= ($i == $page) ? 'active' : ''; ?>">
                            <a class="page-link" href="?page=<?= $i; ?>"><?= $i; ?></a>
                        </li>
                    <?php endfor; ?>
                </ul>
            </div>

            <!-- Sidebar Widgets Column -->
            <? include("include/sidebar.php") ?>
        </div>
    </div>

    <!-- Bootstrap core JavaScript -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

</body>
</html>
