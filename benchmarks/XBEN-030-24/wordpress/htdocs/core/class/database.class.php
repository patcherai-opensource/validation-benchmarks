<?php
/**
 * Dolibarr ERP & CRM - Database class
 *
 * @package  Dolibarr\Core
 */

class DoliDB
{
    private $db;
    public $prefix = 'llx_';
    public $connected = false;
    public $error = '';
    public $lasterror = '';

    /**
     * Constructor - opens connection
     *
     * @param  string  $host     Host
     * @param  string  $user     User
     * @param  string  $pass     Password
     * @param  string  $name     Database name
     * @param  int     $port     Port
     * @param  string  $prefix   Table prefix
     */
    public function __construct($host, $user, $pass, $name, $port = 3306, $prefix = 'llx_')
    {
        $this->prefix = $prefix;

        $this->db = @new mysqli($host, $user, $pass, $name, $port);

        if ($this->db->connect_error) {
            $this->connected = false;
            $this->error = $this->db->connect_error;
        } else {
            $this->connected = true;
            $this->db->set_charset('utf8');
        }
    }

    /**
     * Execute a SQL query
     *
     * @param  string  $query  SQL query
     * @return mixed           Result object or false
     */
    public function query($query)
    {
        if (!$this->connected) {
            return false;
        }

        $result = $this->db->query($query);
        if ($result === false) {
            $this->lasterror = $this->db->error;
        }
        return $result;
    }

    /**
     * Fetch object from result
     *
     * @param  object  $result  Result from query
     * @return object|null
     */
    public function fetch_object($result)
    {
        if ($result) {
            return $result->fetch_object();
        }
        return null;
    }

    /**
     * Fetch array from result
     *
     * @param  object  $result  Result from query
     * @return array|null
     */
    public function fetch_array($result)
    {
        if ($result) {
            return $result->fetch_assoc();
        }
        return null;
    }

    /**
     * Number of rows in result
     *
     * @param  object  $result  Result from query
     * @return int
     */
    public function num_rows($result)
    {
        if ($result) {
            return $result->num_rows;
        }
        return 0;
    }

    /**
     * Free result
     *
     * @param  object  $result  Result from query
     * @return void
     */
    public function free($result)
    {
        if ($result && $result instanceof mysqli_result) {
            $result->free();
        }
    }

    /**
     * Escape string for SQL
     *
     * @param  string  $str  String to escape
     * @return string
     */
    public function escape($str)
    {
        if (!$this->connected) {
            return addslashes($str);
        }
        return $this->db->real_escape_string($str);
    }

    /**
     * Get last error
     *
     * @return string
     */
    public function lasterror()
    {
        return $this->lasterror ?: $this->error;
    }

    /**
     * Get last insert ID
     *
     * @return int
     */
    public function last_insert_id()
    {
        return $this->db->insert_id;
    }

    /**
     * Get number of affected rows
     *
     * @return int
     */
    public function affected_rows()
    {
        return $this->db->affected_rows;
    }

    /**
     * Begin transaction
     *
     * @return bool
     */
    public function begin()
    {
        return $this->db->begin_transaction();
    }

    /**
     * Commit transaction
     *
     * @return bool
     */
    public function commit()
    {
        return $this->db->commit();
    }

    /**
     * Rollback transaction
     *
     * @return bool
     */
    public function rollback()
    {
        return $this->db->rollback();
    }

    /**
     * Close connection
     *
     * @return void
     */
    public function close()
    {
        if ($this->connected) {
            $this->db->close();
        }
    }
}
