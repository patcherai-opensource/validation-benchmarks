<?php
/**
 * Data module library functions
 * 
 * This file contains functions for managing custom data fields
 */

define('DATA_DIRROOT', dirname(dirname(dirname(__FILE__))));

/**
 * Get a new field instance by type
 * 
 * @param string $type The field type
 * @return object|false Field instance or false if not found
 */
function data_get_field_new($type) {
    $filepath = DATA_DIRROOT . '/mod/data/field/' . $type . '/field.class.php';
    
    if (file_exists($filepath)) {
        require_once($filepath);
        $classname = 'data_field_' . $type;
        if (class_exists($classname)) {
            return new $classname();
        }
    }
    return false;
}

/**
 * Get available field types
 * 
 * @return array List of available field types
 */
function data_get_available_field_types() {
    $fielddir = DATA_DIRROOT . '/mod/data/field';
    $types = array();
    
    if (is_dir($fielddir)) {
        $dirs = scandir($fielddir);
        foreach ($dirs as $dir) {
            if ($dir !== '.' && $dir !== '..' && is_dir($fielddir . '/' . $dir)) {
                $classfile = $fielddir . '/' . $dir . '/field.class.php';
                if (file_exists($classfile)) {
                    $types[] = $dir;
                }
            }
        }
    }
    return $types;
}

/**
 * Validate and process imported field data
 * 
 * @param array $fielddata Array containing field definitions
 * @return array Processed field instances
 */
function data_import_fields($fielddata) {
    $results = array();
    foreach ($fielddata as $field) {
        if (isset($field['type'])) {
            $instance = data_get_field_new($field['type']);
            if ($instance) {
                $results[] = array(
                    'success' => true,
                    'field' => $instance->get_info()
                );
            } else {
                $results[] = array(
                    'success' => false,
                    'error' => 'Field type not found'
                );
            }
        }
    }
    return $results;
}
?>
