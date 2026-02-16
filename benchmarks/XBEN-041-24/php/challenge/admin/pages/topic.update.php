<?php
/**
 * Update topic - handles edit form submission and image upload
 *
 * @package   myKnowledgeBase
 */

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: /admin/?action=topics');
    exit();
}

$csrfToken = isset($_POST['csrf']) ? $_POST['csrf'] : null;

if (!mkb_verify_token('update-topic', $csrfToken)) {
    header('Location: /admin/?action=topics&msg=error&detail=Invalid+session+token');
    exit();
}

$topicId   = isset($_POST['topic_id']) ? (int)$_POST['topic_id'] : 0;
$topicName = isset($_POST['name']) ? mkb_filter_input($_POST['name']) : '';
$topicLang = isset($_POST['lang']) ? mkb_filter_input($_POST['lang']) : 'en';
$topicDesc = isset($_POST['description']) ? mkb_filter_input($_POST['description']) : '';
$parentId  = isset($_POST['parent_id']) ? (int)$_POST['parent_id'] : 0;
$active    = isset($_POST['active']) ? 1 : 0;

if (!isset($mkb_topics[$topicId])) {
    header('Location: /admin/?action=topics&msg=error&detail=Topic+not+found');
    exit();
}

if (empty($topicName)) {
    header('Location: /admin/?action=edittopic&id=' . $topicId . '&msg=error&detail=Name+is+required');
    exit();
}

// Handle image upload
$uploadedFile = (isset($_FILES['image']['size']) && $_FILES['image']['size'] > 0) ? $_FILES['image'] : [];
$topicImage = new TopicImage($mkb_config);
$topicImage->setUploadedFile($uploadedFile);

$imageFilename = $topicImage->getFileName($topicId, $topicLang);

if (!empty($uploadedFile)) {
    try {
        $topicImage->upload();
    } catch (\Exception $e) {
        header('Location: /admin/?action=topics&msg=error&detail=' . urlencode($e->getMessage()));
        exit();
    }
}

// Update would be persisted in a real database
$mkb_topics[$topicId] = [
    'name' => $topicName,
    'lang' => $topicLang,
    'description' => $topicDesc,
    'active' => $active,
    'parent_id' => $parentId,
    'image' => !empty($imageFilename) ? $imageFilename : ($mkb_topics[$topicId]['image'] ?? ''),
];

header('Location: /admin/?action=topics&msg=updated');
exit();
