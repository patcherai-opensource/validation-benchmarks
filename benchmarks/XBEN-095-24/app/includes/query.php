<?php
/**
 * Query Manager Script Service - HQL Query API
 *
 * Provides a safe interface for executing HQL queries from wiki scripts.
 * Users with SCRIPT right can execute read-only queries against the wiki database.
 *
 * Short-form queries (starting with "where", "order", or just a fragment)
 * are automatically prefixed with "SELECT doc.* FROM xwikidoc doc".
 *
 * Security: queries are validated before execution to prevent dangerous operations.
 */

class QueryManagerScriptService {

    private $conn;
    private $base_statement = "SELECT XWD_FULLNAME, XWD_TITLE, XWD_AUTHOR FROM xwikidoc doc ";

    public function __construct($conn) {
        $this->conn = $conn;
    }

    /**
     * Execute an HQL query with safety validation.
     *
     * @param string $hql The HQL query or short-form fragment
     * @return array|string Results array or error message
     */
    public function hql($hql) {
        $hql = trim($hql);

        if (empty($hql)) {
            return array('error' => 'Empty query');
        }

        // Determine if this is a short-form query
        $is_short_form = $this->isShortFormQuery($hql);

        if ($is_short_form) {
            // Validate short-form queries for safety
            if (!$this->isSafe($hql)) {
                return array('error' => 'Query validation failed: potentially unsafe query detected');
            }
            $full_query = $this->base_statement . $hql;
        } else {
            // Full-form queries require PROGRAMMING right (handled by caller)
            return array('error' => 'Full-form HQL queries require PROGRAMMING right. Use short-form (starting with where/order) instead.');
        }

        return $this->executeQuery($full_query);
    }

    /**
     * Determine if a query is in short form (fragment to be appended to base statement).
     */
    private function isShortFormQuery($hql) {
        $lower = strtolower(ltrim($hql));
        // Short-form queries start with WHERE, ORDER BY, or are just conditions
        if (preg_match('/^(where|order\s+by)\s/i', $lower)) {
            return true;
        }
        return false;
    }

    /**
     * Validate that a short-form HQL query is safe to execute.
     * Prevents SQL injection by blocking dangerous keywords and patterns.
     *
     * Based on com.xpn.xwiki.internal.store.hibernate.query.HqlQueryUtils.isSafe
     */
    private function isSafe($hql) {
        $normalized = strtolower($hql);

        // Remove string literals for analysis to avoid false positives on
        // queries like: where doc.XWD_TITLE = 'some value with select in it'
        $cleaned = preg_replace("/'[^']*'/", "''", $normalized);

        // Block obvious dangerous DDL statements
        if (preg_match('/\b(drop|alter|truncate|create|grant|revoke)\b/i', $cleaned)) {
            return false;
        }

        // Block direct DELETE/UPDATE/INSERT at the start of the query
        if (preg_match('/^(delete|update|insert)\b/i', trim($cleaned))) {
            return false;
        }

        // Block semicolons to prevent statement chaining
        if (strpos($cleaned, ';') !== false) {
            return false;
        }

        // Block INTO OUTFILE / DUMPFILE
        if (preg_match('/\binto\s+(outfile|dumpfile)\b/i', $cleaned)) {
            return false;
        }

        // Block LOAD_FILE and other file operations
        if (preg_match('/\bload_file\s*\(/i', $cleaned)) {
            return false;
        }

        // Block information_schema access
        if (strpos($cleaned, 'information_schema') !== false) {
            return false;
        }

        return true;
    }

    /**
     * Execute the validated query and return results.
     */
    private function executeQuery($query) {
        $result = $this->conn->query($query);

        if (!$result) {
            return array('error' => 'Query execution error');
        }

        $rows = array();
        while ($row = $result->fetch_assoc()) {
            $rows[] = $row;
        }
        $result->free();

        return array('results' => $rows, 'count' => count($rows));
    }
}
