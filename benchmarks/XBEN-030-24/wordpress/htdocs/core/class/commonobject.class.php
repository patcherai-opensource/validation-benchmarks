<?php
/**
 * Dolibarr ERP & CRM - CommonObject class
 *
 * Parent class of all business objects
 *
 * @package  Dolibarr\Core
 */

require_once __DIR__.'/../lib/functions.lib.php';

class CommonObject
{
    public $db;
    public $id;
    public $table_element = '';
    public $array_options = array();
    public $error = '';
    public $errors = array();

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
     * Load optional (extra) fields values from database into $this->array_options
     * Also computes the value of computed fields.
     *
     * @param  int     $rowid       ID of object
     * @param  string  $optionsArray Additional options
     * @return int                   >0 if OK, <0 if error
     */
    public function fetch_optionals($rowid = null, $optionsArray = null)
    {
        global $extrafields;

        if (empty($rowid)) {
            $rowid = $this->id;
        }

        if (!is_object($extrafields)) {
            require_once __DIR__.'/extrafields.class.php';
            $extrafields = new ExtraFields($this->db);
        }

        // Load extrafields definitions
        $extrafields->fetch_name_optionals_label($this->table_element);

        // Load stored optional values from database
        $table = $this->db->prefix.$this->table_element.'_extrafields';
        $sql = "SELECT * FROM ".$table." WHERE fk_object = ".(int) $rowid;
        $result = @$this->db->query($sql);
        if ($result) {
            $obj = $this->db->fetch_object($result);
            if ($obj) {
                if (!empty($extrafields->attributes[$this->table_element]['label'])) {
                    foreach ($extrafields->attributes[$this->table_element]['label'] as $key => $val) {
                        if (property_exists($obj, $key)) {
                            $this->array_options['options_'.$key] = $obj->$key;
                        }
                    }
                }
            }
            $this->db->free($result);
        }

        // Evaluate computed fields
        if (!empty($extrafields->attributes[$this->table_element]['computed'])) {
            foreach ($extrafields->attributes[$this->table_element]['computed'] as $key => $val) {
                if (!empty($val)) {
                    $object = $this;  // Make available for expression
                    $value = dol_eval($val, 1, 0, '2');
                    $this->array_options['options_'.$key] = $value;
                }
            }
        }

        return 1;
    }

    /**
     * Insert extra field values into database
     *
     * @return int  >0 if OK, <0 if error
     */
    public function insertExtraFields()
    {
        global $extrafields;

        if (!is_object($extrafields)) {
            require_once __DIR__.'/extrafields.class.php';
            $extrafields = new ExtraFields($this->db);
        }

        $extrafields->fetch_name_optionals_label($this->table_element);

        $table = $this->db->prefix.$this->table_element.'_extrafields';

        // Check if row exists
        $sql = "SELECT COUNT(*) as cnt FROM ".$table." WHERE fk_object = ".(int) $this->id;
        $result = @$this->db->query($sql);
        $exists = false;
        if ($result) {
            $obj = $this->db->fetch_object($result);
            $exists = ($obj->cnt > 0);
        }

        if (!$exists) {
            $sql = "INSERT INTO ".$table." (fk_object) VALUES (".(int) $this->id.")";
            @$this->db->query($sql);
        }

        return 1;
    }

    /**
     * Show extra fields in output format
     *
     * @param  ExtraFields $extrafields  ExtraFields object
     * @param  string      $mode         'view' or 'edit'
     * @return string                     HTML output
     */
    public function showOptionals($extrafields, $mode = 'view')
    {
        $out = '';
        if (!empty($extrafields->attributes[$this->table_element]['label'])) {
            foreach ($extrafields->attributes[$this->table_element]['label'] as $key => $label) {
                $value = isset($this->array_options['options_'.$key]) ? $this->array_options['options_'.$key] : '';
                $out .= '<tr class="field_extra_'.$key.'">';
                $out .= '<td class="titlefield">'.dol_escape_htmltag($label).'</td>';
                $out .= '<td>'.dol_escape_htmltag($value).'</td>';
                $out .= '</tr>';
            }
        }
        return $out;
    }
}
