<?php
// Number field handler
$field_name = "Number";
$field_description = "A numeric input field for integer or decimal values.";
$field_icon = "🔢";

function render_field($value = '') {
    return '<input type="number" class="form-control" value="' . htmlspecialchars($value) . '">';
}

function validate_field($value) {
    return is_numeric($value);
}
?>
