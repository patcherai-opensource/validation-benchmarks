<?php
// Text field handler
$field_name = "Text";
$field_description = "A simple text input field for short text entries.";
$field_icon = "📝";

function render_field($value = '') {
    return '<input type="text" class="form-control" value="' . htmlspecialchars($value) . '">';
}

function validate_field($value) {
    return strlen($value) <= 255;
}
?>
