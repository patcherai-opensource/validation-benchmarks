<?php
/**
 * Grid helper utilities for ExtJS-compatible data grids.
 * Extracts sorting and filtering configuration from request parameters.
 */

/**
 * Extract sorting settings from request parameters.
 * Expects a JSON-encoded 'sort' parameter with property and direction.
 *
 * @param array $params Request parameters
 * @return array [orderKey => string|null, order => string|null]
 */
function extractSortingSettings($params) {
    $orderKey = null;
    $order = null;

    $sortParam = isset($params['sort']) ? $params['sort'] : false;
    if ($sortParam) {
        $sortParam = json_decode($sortParam, true);
        if (is_array($sortParam) && isset($sortParam[0])) {
            $sortParam = $sortParam[0];

            if (isset($sortParam['property'])) {
                $orderKey = $sortParam['property'];
                $order = isset($sortParam['direction']) ? $sortParam['direction'] : 'ASC';
            }
        }
    }

    return array('orderKey' => $orderKey, 'order' => $order);
}

/**
 * Build a filter condition string from ExtJS-compatible filter definitions.
 *
 * @param string $filterString JSON-encoded filter array
 * @param mysqli $conn Database connection for escaping
 * @return string SQL condition string
 */
function buildFilterCondition($filterString, $conn) {
    if (empty($filterString)) {
        return '';
    }

    $filters = json_decode($filterString, true);
    if (!is_array($filters)) {
        return '';
    }

    $conditions = array();
    foreach ($filters as $f) {
        $field = $conn->real_escape_string($f['field']);
        $value = $conn->real_escape_string($f['value']);

        switch ($f['type']) {
            case 'string':
                $conditions[] = "`$field` LIKE '%$value%'";
                break;
            case 'numeric':
                $op = '=';
                if (isset($f['comparison'])) {
                    if ($f['comparison'] === 'lt') $op = '<';
                    elseif ($f['comparison'] === 'gt') $op = '>';
                }
                $conditions[] = "`$field` $op '$value'";
                break;
        }
    }

    return implode(' AND ', $conditions);
}
