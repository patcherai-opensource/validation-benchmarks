<?php
$course_id = isset($_GET['id']) ? (int)$_GET['id'] : 0;
$json_data = file_get_contents('courses.json');
$courses = json_decode($json_data, true);

$course = null;
foreach ($courses as $c) {
    if ($c['id'] === $course_id) {
        $course = $c;
        break;
    }
}

if (!$course) {
    header("Location: index.php");
    exit;
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>EduLearn LMS - <?= htmlspecialchars($course['title']) ?></title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <? include("include/navigation-bar.php") ?>

    <header class="py-4 bg-light border-bottom mb-4">
        <div class="container">
            <h2 class="fw-bolder"><?= htmlspecialchars($course['title']) ?></h2>
            <p class="lead mb-0"><?= htmlspecialchars($course['category']) ?> | Instructor: <?= htmlspecialchars($course['instructor']) ?></p>
        </div>
    </header>

    <div class="container">
        <div class="row">
            <div class="col-md-8">
                <div class="card mb-4">
                    <img class="card-img-top" src="<?= htmlspecialchars($course['image_url']) ?>" alt="Course Image">
                    <div class="card-body">
                        <h5>Course Description</h5>
                        <p><?= htmlspecialchars($course['description']) ?></p>
                        <hr>
                        <h5>Course Content</h5>
                        <ul>
                            <li>Module 1: Introduction and Overview</li>
                            <li>Module 2: Core Concepts</li>
                            <li>Module 3: Practical Applications</li>
                            <li>Module 4: Advanced Topics</li>
                            <li>Module 5: Final Assessment</li>
                        </ul>
                        <hr>
                        <a href="index.php" class="btn btn-secondary">Back to Courses</a>
                        <button class="btn btn-primary" disabled>Enroll Now</button>
                    </div>
                </div>
            </div>

            <? include("include/sidebar.php") ?>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
