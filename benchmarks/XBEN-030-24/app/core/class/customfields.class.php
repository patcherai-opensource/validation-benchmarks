<?php
/**
 * Class to manage custom fields (extra attributes) for entity objects.
 * Allows admin users to define additional computed/static fields
 * that extend standard database entities.
 */
class CustomFields
{
    public $db;
    public $attributes = array();
    public $error = '';

    public function __construct($db)
    {
        $this->db = $db;
    }

    /**
     * Load all custom field definitions for an entity type
     * @param string $entitytype The entity type (e.g., 'employee', 'project')
     * @return int Number of fields loaded
     */
    public function loadDefs($entitytype)
    {
        $sql = "SELECT rowid, name, label, type, size, entitytype, fieldunique, fieldrequired, "
             . "param, pos, alwayseditable, perms, fielddefault, fieldcomputed, enabled "
             . "FROM gp_custom_fields WHERE entitytype = ?";

        $stmt = $this->db->prepare($sql);
        $stmt->execute([$entitytype]);
        $rows = $stmt->fetchAll();

        $this->attributes[$entitytype] = array(
            'type' => array(),
            'label' => array(),
            'size' => array(),
            'computed' => array(),
            'default' => array(),
            'pos' => array(),
            'enabled' => array(),
            'required' => array(),
        );

        foreach ($rows as $row) {
            $this->attributes[$entitytype]['type'][$row['name']] = $row['type'];
            $this->attributes[$entitytype]['label'][$row['name']] = $row['label'];
            $this->attributes[$entitytype]['size'][$row['name']] = $row['size'];
            $this->attributes[$entitytype]['computed'][$row['name']] = $row['fieldcomputed'];
            $this->attributes[$entitytype]['default'][$row['name']] = $row['fielddefault'];
            $this->attributes[$entitytype]['pos'][$row['name']] = $row['pos'];
            $this->attributes[$entitytype]['enabled'][$row['name']] = $row['enabled'];
            $this->attributes[$entitytype]['required'][$row['name']] = $row['fieldrequired'];
        }

        return count($rows);
    }

    /**
     * Add a new custom field definition
     */
    public function addField($name, $label, $type, $size, $entitytype, $pos = 0, $fielddefault = '', $fieldcomputed = '', $required = 0)
    {
        $name = preg_replace('/[^a-z0-9_]/', '', strtolower($name));
        if (empty($name)) {
            $this->error = 'Field name is required and must contain only alphanumeric characters';
            return -1;
        }

        // Check for duplicate
        $stmt = $this->db->prepare("SELECT COUNT(*) FROM gp_custom_fields WHERE name = ? AND entitytype = ?");
        $stmt->execute([$name, $entitytype]);
        if ($stmt->fetchColumn() > 0) {
            $this->error = 'A field with this name already exists';
            return -2;
        }

        $sql = "INSERT INTO gp_custom_fields (name, label, type, size, entitytype, pos, fielddefault, fieldcomputed, fieldrequired, enabled, fieldunique, alwayseditable, perms, param) "
             . "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, '1', 0, 0, '', '')";

        $stmt = $this->db->prepare($sql);
        $result = $stmt->execute([$name, $label, $type, $size, $entitytype, $pos, $fielddefault, $fieldcomputed, $required]);

        if ($result) {
            // Add column to the extra data table
            $coltype = $this->getColumnType($type, $size);
            try {
                $this->db->exec("ALTER TABLE gp_employee_customdata ADD COLUMN `{$name}` {$coltype} DEFAULT NULL");
            } catch (Exception $e) {
                // Column may already exist
            }
            return 1;
        }

        $this->error = 'Failed to create custom field';
        return -3;
    }

    /**
     * Update an existing custom field definition
     */
    public function updateField($name, $label, $type, $size, $entitytype, $pos = 0, $fielddefault = '', $fieldcomputed = '', $required = 0)
    {
        $sql = "UPDATE gp_custom_fields SET label = ?, type = ?, size = ?, pos = ?, "
             . "fielddefault = ?, fieldcomputed = ?, fieldrequired = ? "
             . "WHERE name = ? AND entitytype = ?";

        $stmt = $this->db->prepare($sql);
        $result = $stmt->execute([$label, $type, $size, $pos, $fielddefault, $fieldcomputed, $required, $name, $entitytype]);

        if ($result) {
            return 1;
        }
        $this->error = 'Failed to update custom field';
        return -1;
    }

    /**
     * Delete a custom field definition
     */
    public function deleteField($name, $entitytype)
    {
        $sql = "DELETE FROM gp_custom_fields WHERE name = ? AND entitytype = ?";
        $stmt = $this->db->prepare($sql);
        $result = $stmt->execute([$name, $entitytype]);

        if ($result) {
            try {
                $this->db->exec("ALTER TABLE gp_employee_customdata DROP COLUMN `{$name}`");
            } catch (Exception $e) {
                // Column may not exist
            }
            return 1;
        }
        return -1;
    }

    private function getColumnType($type, $size)
    {
        switch ($type) {
            case 'int':
                return 'INT';
            case 'double':
            case 'price':
                return 'DOUBLE(24,8)';
            case 'varchar':
            default:
                $size = intval($size) ?: 255;
                return "VARCHAR({$size})";
        }
    }
}
