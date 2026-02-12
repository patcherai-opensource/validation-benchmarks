<?php
/**
 * Dolibarr ERP & CRM - ExtraFields class
 *
 * Class to manage extra fields configuration
 *
 * @package  Dolibarr\Core
 */

class ExtraFields
{
    public $db;
    public $error = '';
    public $errors = array();
    public $attributes = array();

    /**
     * Constructor
     *
     * @param  object  $db  Database handler
     */
    public function __construct($db)
    {
        $this->db = $db;
    }

    /**
     * Load definition of extra fields for a given element type
     *
     * @param  string  $elementtype  Element type ('user', 'societe', 'product', etc.)
     * @param  bool    $forceload    Force reload from database
     * @return int                    Number of attributes loaded, <0 if error
     */
    public function fetch_name_optionals_label($elementtype, $forceload = false)
    {
        if (isset($this->attributes[$elementtype]) && !$forceload) {
            return count($this->attributes[$elementtype]['label']);
        }

        $this->attributes[$elementtype] = array(
            'type'     => array(),
            'label'    => array(),
            'size'     => array(),
            'computed' => array(),
            'default'  => array(),
            'enabled'  => array(),
            'list'     => array(),
            'pos'      => array(),
            'help'     => array(),
            'required' => array(),
            'langfile' => array(),
        );

        $sql = "SELECT rowid, name, label, type, size, fielddefault, fieldcomputed, fieldrequired, pos, enabled, list, help, langs";
        $sql .= " FROM ".$this->db->prefix."extrafields";
        $sql .= " WHERE elementtype = '".$this->db->escape($elementtype)."'";
        $sql .= " ORDER BY pos ASC";

        $result = $this->db->query($sql);
        if ($result) {
            $count = 0;
            while ($obj = $this->db->fetch_object($result)) {
                $fieldname = $obj->name;
                $this->attributes[$elementtype]['type'][$fieldname]     = $obj->type;
                $this->attributes[$elementtype]['label'][$fieldname]    = $obj->label;
                $this->attributes[$elementtype]['size'][$fieldname]     = $obj->size;
                $this->attributes[$elementtype]['computed'][$fieldname] = $obj->fieldcomputed;
                $this->attributes[$elementtype]['default'][$fieldname]  = $obj->fielddefault;
                $this->attributes[$elementtype]['enabled'][$fieldname]  = $obj->enabled;
                $this->attributes[$elementtype]['list'][$fieldname]     = $obj->list;
                $this->attributes[$elementtype]['pos'][$fieldname]      = $obj->pos;
                $this->attributes[$elementtype]['help'][$fieldname]     = $obj->help;
                $this->attributes[$elementtype]['required'][$fieldname] = $obj->fieldrequired;
                $this->attributes[$elementtype]['langfile'][$fieldname] = $obj->langs;
                $count++;
            }
            $this->db->free($result);
            return $count;
        } else {
            $this->error = $this->db->lasterror();
            return -1;
        }
    }

    /**
     * Add a new extra field definition
     *
     * @param  string  $attrname       Attribute name
     * @param  string  $label          Label
     * @param  string  $type           Type (varchar, int, double, text, computed, ...)
     * @param  int     $pos            Position
     * @param  string  $size           Size
     * @param  string  $elementtype    Element type
     * @param  int     $required       1 if required
     * @param  string  $default_value  Default value
     * @param  string  $computed       Computed formula
     * @param  int     $enabled        1=always, 0=hidden
     * @param  int     $list           List display setting
     * @param  string  $help           Help text
     * @param  string  $langfile       Language file
     * @return int                      >0 if OK, <0 if error
     */
    public function addExtraField($attrname, $label, $type, $pos, $size, $elementtype, $required = 0, $default_value = '', $computed = '', $enabled = 1, $list = 1, $help = '', $langfile = '')
    {
        if (empty($attrname) || empty($label) || empty($type)) {
            $this->error = 'ErrorMandatoryFieldMissing';
            return -1;
        }

        // Check attribute name format
        if (!preg_match('/^[a-z][a-z0-9_]*$/i', $attrname)) {
            $this->error = 'ErrorBadAttributeName';
            return -2;
        }

        $sql = "INSERT INTO ".$this->db->prefix."extrafields";
        $sql .= " (name, label, type, pos, size, elementtype, fieldrequired, fielddefault, fieldcomputed, enabled, list, help, langs)";
        $sql .= " VALUES (";
        $sql .= "'".$this->db->escape($attrname)."',";
        $sql .= "'".$this->db->escape($label)."',";
        $sql .= "'".$this->db->escape($type)."',";
        $sql .= (int) $pos.",";
        $sql .= "'".$this->db->escape($size)."',";
        $sql .= "'".$this->db->escape($elementtype)."',";
        $sql .= (int) $required.",";
        $sql .= "'".$this->db->escape($default_value)."',";
        $sql .= "'".$this->db->escape($computed)."',";
        $sql .= (int) $enabled.",";
        $sql .= (int) $list.",";
        $sql .= "'".$this->db->escape($help)."',";
        $sql .= "'".$this->db->escape($langfile)."'";
        $sql .= ")";

        $result = $this->db->query($sql);
        if ($result) {
            // Also create the column in the target table if not computed
            if ($type != 'computed') {
                $this->createExtraFieldColumn($attrname, $type, $size, $elementtype);
            }
            return 1;
        } else {
            $this->error = $this->db->lasterror();
            return -3;
        }
    }

    /**
     * Update an extra field definition
     *
     * @param  string  $attrname    Attribute name
     * @param  string  $label       Label
     * @param  string  $type        Type
     * @param  int     $pos         Position
     * @param  string  $size        Size
     * @param  string  $elementtype Element type
     * @param  int     $required    Required flag
     * @param  string  $default     Default value
     * @param  string  $computed    Computed formula
     * @param  int     $enabled     Enabled flag
     * @param  int     $list        List setting
     * @param  string  $help        Help text
     * @return int                   >0 if OK, <0 if error
     */
    public function updateExtraField($attrname, $label = '', $type = '', $pos = 0, $size = '', $elementtype = '', $required = 0, $default = '', $computed = '', $enabled = 1, $list = 1, $help = '')
    {
        $sql = "UPDATE ".$this->db->prefix."extrafields SET";

        $updates = array();
        if ($label !== '') {
            $updates[] = " label = '".$this->db->escape($label)."'";
        }
        if ($type !== '') {
            $updates[] = " type = '".$this->db->escape($type)."'";
        }
        $updates[] = " pos = ".(int) $pos;
        if ($size !== '') {
            $updates[] = " size = '".$this->db->escape($size)."'";
        }
        $updates[] = " fieldrequired = ".(int) $required;
        $updates[] = " fielddefault = '".$this->db->escape($default)."'";
        $updates[] = " fieldcomputed = '".$this->db->escape($computed)."'";
        $updates[] = " enabled = ".(int) $enabled;
        $updates[] = " list = ".(int) $list;
        $updates[] = " help = '".$this->db->escape($help)."'";

        $sql .= implode(',', $updates);
        $sql .= " WHERE name = '".$this->db->escape($attrname)."'";
        $sql .= " AND elementtype = '".$this->db->escape($elementtype)."'";

        $result = $this->db->query($sql);
        if ($result) {
            return 1;
        } else {
            $this->error = $this->db->lasterror();
            return -1;
        }
    }

    /**
     * Delete an extra field definition
     *
     * @param  string  $attrname    Attribute name
     * @param  string  $elementtype Element type
     * @return int                   >0 if OK, <0 if error
     */
    public function deleteExtraField($attrname, $elementtype)
    {
        $sql = "DELETE FROM ".$this->db->prefix."extrafields";
        $sql .= " WHERE name = '".$this->db->escape($attrname)."'";
        $sql .= " AND elementtype = '".$this->db->escape($elementtype)."'";

        $result = $this->db->query($sql);
        if ($result) {
            return 1;
        }
        $this->error = $this->db->lasterror();
        return -1;
    }

    /**
     * Create column in the object table for the extra field
     *
     * @param  string  $attrname    Attribute name
     * @param  string  $type        Type
     * @param  string  $size        Size
     * @param  string  $elementtype Element type
     * @return void
     */
    private function createExtraFieldColumn($attrname, $type, $size, $elementtype)
    {
        $table = $this->db->prefix.$elementtype.'_extrafields';
        $coltype = 'varchar(255)';
        if ($type == 'int') {
            $coltype = 'int';
        } elseif ($type == 'double') {
            $coltype = 'double(24,8)';
        } elseif ($type == 'text') {
            $coltype = 'text';
        } elseif ($type == 'boolean') {
            $coltype = 'int';
        } elseif ($type == 'date') {
            $coltype = 'date';
        }

        $sql = "ALTER TABLE ".$table." ADD COLUMN ".$this->db->escape($attrname)." ".$coltype." DEFAULT NULL";
        @$this->db->query($sql); // Ignore error if column already exists
    }
}
