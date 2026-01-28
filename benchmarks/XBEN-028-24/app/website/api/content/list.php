<?php
header('Content-Type: application/json');

// Simulated content listing API
$response = array(
    "status" => "success",
    "version" => "2.3.1-legacy",
    "data" => array(
        "content_types" => array(
            array("id" => 1, "name" => "article", "fields" => array("title", "body", "author")),
            array("id" => 2, "name" => "blog_post", "fields" => array("title", "content", "tags")),
            array("id" => 3, "name" => "media", "fields" => array("title", "description", "ezbinaryfile")),
            array("id" => 4, "name" => "landing_page", "fields" => array("title", "blocks", "layout"))
        ),
        "total_content" => 847,
        "storage" => array(
            "media_path" => "/posts/uploads/",
            "max_upload_size" => "10MB"
        )
    )
);

echo json_encode($response, JSON_PRETTY_PRINT);
?>
