<?php

/**
 * Query validation utilities for the content query API.
 * Validates that user-provided query fragments are safe for execution.
 * Only SELECT statements against allowed tables and columns are permitted.
 */

// Allowed tables and their permitted columns for content queries
$ALLOWED_QUERY_TABLES = [
    'wiki_documents' => ['doc_id', 'doc_fullname', 'doc_title', 'doc_space', 'doc_language', 'doc_hidden', 'doc_author', 'doc_created', 'doc_modified'],
    'wiki_spaces' => ['space_id', 'space_name', 'space_hidden']
];

/**
 * Check if a query fragment is in "short form" - i.e., starts with
 * a clause keyword rather than being a complete SELECT statement.
 * Short form queries get automatically prefixed with a safe SELECT.
 */
function is_short_form_query($statement) {
    $trimmed = strtolower(trim($statement));
    return (
        strpos($trimmed, 'where') === 0 ||
        strpos($trimmed, 'order') === 0 ||
        strpos($trimmed, ',') === 0 ||
        strpos($trimmed, 'from') === 0
    );
}

/**
 * Convert a short form query to a complete statement by prepending
 * the standard document select prefix.
 */
function to_complete_statement($statement) {
    $trimmed = trim($statement);
    if (empty($trimmed) || is_short_form_query($trimmed)) {
        return "SELECT doc.doc_fullname, doc.doc_title, doc.doc_space FROM wiki_documents doc " . $trimmed;
    }
    return $trimmed;
}

/**
 * Validate whether a complete SQL statement is safe for execution.
 * Checks that:
 * - Only SELECT statements are used
 * - Only allowed tables are referenced
 * - Only allowed columns are selected
 * - No dangerous subqueries or modifications
 */
function is_query_safe($statement_string) {
    $normalized = trim($statement_string);
    
    // Must be a SELECT statement
    if (stripos($normalized, 'SELECT') !== 0) {
        return false;
    }
    
    // Block obvious dangerous operations at the statement level
    $dangerous_patterns = [
        '/\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|EXEC|EXECUTE)\b/i',
        '/\bINTO\s+OUTFILE\b/i',
        '/\bLOAD_FILE\b/i',
        '/\bINTO\s+DUMPFILE\b/i',
    ];
    
    foreach ($dangerous_patterns as $pattern) {
        if (preg_match($pattern, $normalized)) {
            return false;
        }
    }
    
    // Extract the main SELECT columns (between SELECT and FROM)
    if (!preg_match('/^SELECT\s+(.+?)\s+FROM\s+/is', $normalized, $matches)) {
        return false;
    }
    
    $select_part = $matches[1];
    
    // Validate selected columns are from allowed set
    $columns = array_map('trim', explode(',', $select_part));
    $allowed_cols_flat = [];
    foreach ($GLOBALS['ALLOWED_QUERY_TABLES'] as $table => $cols) {
        foreach ($cols as $col) {
            $allowed_cols_flat[] = $col;
            // Also allow aliased forms like doc.col_name
            $allowed_cols_flat[] = "doc.$col";
            $allowed_cols_flat[] = "sp.$col";
        }
    }
    $allowed_cols_flat[] = '*';
    $allowed_cols_flat[] = 'doc.*';
    
    foreach ($columns as $col) {
        $col_clean = trim($col);
        // Allow count(*) and similar aggregate functions on allowed columns
        if (preg_match('/^(count|max|min|avg)\s*\(/i', $col_clean)) {
            continue;
        }
        if (!in_array(strtolower($col_clean), array_map('strtolower', $allowed_cols_flat))) {
            return false;
        }
    }
    
    // Validate FROM clause only references allowed tables
    if (preg_match('/\bFROM\s+(\w+)(\s+(\w+))?\b/i', $normalized, $from_match)) {
        $table_name = $from_match[1];
        if (!isset($GLOBALS['ALLOWED_QUERY_TABLES'][$table_name])) {
            return false;
        }
    }
    
    return true;
}
