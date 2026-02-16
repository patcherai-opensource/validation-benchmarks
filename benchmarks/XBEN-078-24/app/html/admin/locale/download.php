<?php
require_once __DIR__ . '/../auth.php';
requireAdmin();

$conn = getDbConnection();

$domain = isset($_GET['domain']) ? $_GET['domain'] : 'messages';
$validDomains = ['messages', 'admin'];
if (!in_array($domain, $validDomains)) {
    header('HTTP/1.1 400 Bad Request');
    echo json_encode(['success' => false, 'message' => 'Invalid domain']);
    exit;
}

$tableName = 'translations_' . $domain;
$validLanguages = ['en', 'de', 'fr'];

$condition = buildGridFilterCondition($conn, $tableName, $validLanguages);

$sql = "SELECT DISTINCT t1.`key`, t1.`type`, t1.`creationDate`, t1.`modificationDate`";
foreach ($validLanguages as $lang) {
    $escapedLang = $conn->real_escape_string($lang);
    $sql .= ", (SELECT t2.text FROM {$tableName} t2 WHERE t2.`key` = t1.`key` AND t2.language = '{$escapedLang}') AS `{$lang}`";
}
$sql .= " FROM {$tableName} t1";

if ($condition) {
    $sql .= " WHERE " . $condition;
}
$sql .= " GROUP BY t1.`key` ORDER BY t1.`key` ASC";

$result = $conn->query($sql);

if ($result === false) {
    header('HTTP/1.1 500 Internal Server Error');
    echo json_encode(['success' => false, 'message' => 'Export failed']);
    exit;
}

$translations = [];
while ($row = $result->fetch_assoc()) {
    $translations[] = $row;
}

$columns = array_merge(['key'], $validLanguages);

$headerRow = [];
foreach ($columns as $col) {
    $headerRow[] = '"' . $col . '"';
}
$csv = implode(';', $headerRow) . "\r\n";

foreach ($translations as $t) {
    $tempRow = [];
    foreach ($columns as $col) {
        $value = isset($t[$col]) ? $t[$col] : '';
        if (is_string($value)) {
            $value = str_replace(["\r", "\n"], ' ', $value);
            $value = str_replace('"', '&quot;', $value);
            $tempRow[] = '"' . $value . '"';
        } else {
            $tempRow[] = $value;
        }
    }
    $csv .= implode(';', $tempRow) . "\r\n";
}

$conn->close();

header('Content-Type: text/csv; charset=UTF-8');
header('Content-Disposition: attachment; filename="export_' . $domain . '_translations.csv"');
header('Content-Encoding: UTF-8');
echo "\xEF\xBB\xBF" . $csv;
exit;


/**
 * Build filter conditions from the grid filter JSON parameter.
 * Applies column-level filtering based on provided filter criteria.
 */
function buildGridFilterCondition($conn, $tableName, $validLanguages) {
    $conditionFilters = [];

    $filterJson = isset($_GET['filter']) ? $_GET['filter'] : null;
    if ($filterJson) {
        $filters = json_decode($filterJson, true);
        if (!is_array($filters)) {
            return null;
        }

        foreach ($filters as $filter) {
            $operator = '=';
            $field = null;
            $value = null;

            $fieldname = isset($filter['property']) ? $filter['property'] : null;
            if (!$fieldname) {
                continue;
            }

            if (in_array(ltrim($fieldname, '_'), $validLanguages)) {
                $fieldname = ltrim($fieldname, '_');
            }

            if (in_array($fieldname, $validLanguages)) {
                continue;
            }

            $fieldname = $tableName . '.' . $fieldname;

            if (!empty($filter['value'])) {
                if (isset($filter['type']) && $filter['type'] === 'string') {
                    $operator = 'LIKE';
                    $field = $fieldname;
                    $value = '%' . $filter['value'] . '%';
                } elseif (isset($filter['type']) && $filter['type'] === 'date'
                    || in_array($fieldname, ['modificationDate', 'creationDate'])) {
                    if (isset($filter['operator'])) {
                        if ($filter['operator'] === 'lt') {
                            $operator = '<';
                        } elseif ($filter['operator'] === 'gt') {
                            $operator = '>';
                        } elseif ($filter['operator'] === 'eq') {
                            $operator = '=';
                            $fieldname = "UNIX_TIMESTAMP(DATE(FROM_UNIXTIME({$fieldname})))";
                        }
                    }
                    $filter['value'] = strtotime($filter['value']);
                    $field = $fieldname;
                    $value = $filter['value'];
                } elseif (isset($filter['type']) && $filter['type'] === 'numeric') {
                    $field = $fieldname;
                    $value = $filter['value'];
                }
            }

            if ($field && $value) {
                $condition = $field . ' ' . $operator . ' ' . "'" . $conn->real_escape_string($value) . "'";
                $conditionFilters[] = $condition;
            }
        }
    }

    if (isset($_GET['searchString']) && !empty($_GET['searchString'])) {
        $searchTerm = "'" . $conn->real_escape_string('%' . mb_strtolower($_GET['searchString']) . '%') . "'";
        $conditionFilters[] = "(LOWER({$tableName}.`key`) LIKE {$searchTerm} OR LOWER({$tableName}.text) LIKE {$searchTerm})";
    }

    if (!empty($conditionFilters)) {
        return implode(' AND ', $conditionFilters);
    }

    return null;
}
