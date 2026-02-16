<?php
/**
 * Save new topic - handles form submission and image upload
 *
 * @package   myKnowledgeBase
 */

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: /admin/?action=topics');
    exit();
}

$csrfToken = isset($_POST['csrf']) ? $_POST['csrf'] : null;

if (!mkb_verify_token('save-topic', $csrfToken)) {
    header('Location: /admin/?action=topics&msg=error&detail=Invalid+session+token');
    exit();
}

// Process topic data
$topicName = isset($_POST['name']) ? mkb_filter_input($_POST['name']) : '';
$topicLang = isset($_POST['lang']) ? mkb_filter_input($_POST['lang']) : 'en';
$topicDesc = isset($_POST['description']) ? mkb_filter_input($_POST['description']) : '';
$parentId  = isset($_POST['parent_id']) ? (int)$_POST['parent_id'] : 0;
$active    = isset($_POST['active']) ? 1 : 0;

if (empty($topicName)) {
    header('Location: /admin/?action=addtopic&msg=error&detail=Name+is+required');
    exit();
}

// Generate new topic ID
$topicId = max(array_keys($mkb_topics)) + 1;

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

// In a real application this would be saved to the database
// For this instance, the topic is created in-memory for this request
$mkb_topics[$topicId] = [
    'name' => $topicName,
    'lang' => $topicLang,
    'description' => $topicDesc,
    'active' => $active,
    'parent_id' => $parentId,
    'image' => $imageFilename,
];

header('Location: /admin/?action=topics&msg=saved');
exit();
