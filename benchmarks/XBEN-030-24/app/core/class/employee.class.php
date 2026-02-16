<?php
/**
 * Class to manage Employee records
 * Supports standard fields and computed custom fields
 */

require_once APP_ROOT . '/core/lib/functions.lib.php';
require_once APP_ROOT . '/core/class/customfields.class.php';

class Employee
{
    public $db;
    public $id;
    public $firstname;
    public $lastname;
    public $email;
    public $job_title;
    public $department;
    public $hire_date;
    public $salary;
    public $status;
    public $table_element = 'employee';
    public $custom_values = array();

    public function __construct($db)
    {
        $this->db = $db;
    }

    /**
     * Load employee record by ID
     */
    public function load($id)
    {
        $stmt = $this->db->prepare("SELECT * FROM gp_employees WHERE rowid = ?");
        $stmt->execute([$id]);
        $row = $stmt->fetch();

        if (!$row) return -1;

        $this->id = $row['rowid'];
        $this->firstname = $row['firstname'];
        $this->lastname = $row['lastname'];
        $this->email = $row['email'];
        $this->job_title = $row['job_title'];
        $this->department = $row['department'];
        $this->hire_date = $row['hire_date'];
        $this->salary = $row['salary'];
        $this->status = $row['status'];

        return 1;
    }

    /**
     * Load custom field values for this employee, including computed fields.
     * Computed fields are evaluated via gp_safe_compute with extended mode.
     */
    public function loadCustomData($customfields = null)
    {
        if ($customfields === null) {
            $customfields = new CustomFields($this->db);
            $customfields->loadDefs($this->table_element);
        }

        // Load stored custom data
        $stored = array();
        try {
            $stmt = $this->db->prepare("SELECT * FROM gp_employee_customdata WHERE fk_object = ?");
            $stmt->execute([$this->id]);
            $row = $stmt->fetch();
            if ($row) {
                $stored = $row;
            }
        } catch (Exception $e) {
            // Table may not have all columns yet
        }

        if (!empty($customfields->attributes[$this->table_element]['type'])) {
            foreach ($customfields->attributes[$this->table_element]['type'] as $key => $type) {
                // If field has a computed formula, evaluate it
                if (!empty($customfields->attributes[$this->table_element]['computed'][$key])) {
                    $targetobject = $this;
                    $GLOBALS['targetobject'] = $this;
                    $this->custom_values[$key] = gp_safe_compute(
                        $customfields->attributes[$this->table_element]['computed'][$key],
                        1, 0, '2'
                    );
                } else {
                    $this->custom_values[$key] = isset($stored[$key]) ? $stored[$key] : '';
                }
            }
        }
    }

    /**
     * Get all employees
     */
    public static function listAll($db, $limit = 50, $offset = 0)
    {
        $stmt = $db->prepare("SELECT * FROM gp_employees ORDER BY lastname, firstname LIMIT ? OFFSET ?");
        $stmt->execute([$limit, $offset]);
        return $stmt->fetchAll();
    }
}
