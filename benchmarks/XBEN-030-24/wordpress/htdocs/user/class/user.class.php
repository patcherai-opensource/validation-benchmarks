<?php
/**
 * Dolibarr ERP & CRM - User class
 *
 * @package  Dolibarr\User
 */

require_once __DIR__.'/../../core/class/commonobject.class.php';

class User extends CommonObject
{
    public $table_element = 'user';

    public $id;
    public $login;
    public $pass;
    public $pass_crypted;
    public $lastname;
    public $firstname;
    public $email;
    public $admin;
    public $statut;
    public $entity;
    public $datec;
    public $datem;
    public $note_private;
    public $note_public;
    public $office_phone;
    public $user_mobile;
    public $job;
    public $address;
    public $zip;
    public $town;
    public $fk_country;

    /**
     * Constructor
     *
     * @param  object  $db  Database handler
     */
    public function __construct($db)
    {
        $this->db = $db;
        $this->table_element = 'user';
    }

    /**
     * Load a user from database by ID
     *
     * @param  int     $id     User ID
     * @param  string  $login  Login (alternative to ID)
     * @return int              >0 if OK, <0 if error
     */
    public function fetch($id = 0, $login = '')
    {
        $sql = "SELECT u.rowid, u.login, u.pass_crypted, u.lastname, u.firstname, u.email,";
        $sql .= " u.admin, u.statut, u.entity, u.datec, u.tms as datem,";
        $sql .= " u.note_private, u.note_public, u.office_phone, u.user_mobile,";
        $sql .= " u.job, u.address, u.zip, u.town, u.fk_country";
        $sql .= " FROM ".$this->db->prefix."user as u";

        if ($id > 0) {
            $sql .= " WHERE u.rowid = ".(int) $id;
        } elseif ($login) {
            $sql .= " WHERE u.login = '".$this->db->escape($login)."'";
        } else {
            return -1;
        }

        $result = $this->db->query($sql);
        if ($result) {
            $obj = $this->db->fetch_object($result);
            if ($obj) {
                $this->id           = $obj->rowid;
                $this->login        = $obj->login;
                $this->pass_crypted = $obj->pass_crypted;
                $this->lastname     = $obj->lastname;
                $this->firstname    = $obj->firstname;
                $this->email        = $obj->email;
                $this->admin        = $obj->admin;
                $this->statut       = $obj->statut;
                $this->entity       = $obj->entity;
                $this->datec        = $obj->datec;
                $this->datem        = $obj->datem;
                $this->note_private = $obj->note_private;
                $this->note_public  = $obj->note_public;
                $this->office_phone = $obj->office_phone;
                $this->user_mobile  = $obj->user_mobile;
                $this->job          = $obj->job;
                $this->address      = $obj->address;
                $this->zip          = $obj->zip;
                $this->town         = $obj->town;
                $this->fk_country   = $obj->fk_country;

                $this->db->free($result);

                // Load extra fields
                $this->fetch_optionals($this->id);

                return 1;
            }
            $this->db->free($result);
            return 0;
        }
        $this->error = $this->db->lasterror();
        return -1;
    }

    /**
     * Verify password
     *
     * @param  string  $password  Password to check
     * @return bool
     */
    public function checkPassword($password)
    {
        return password_verify($password, $this->pass_crypted);
    }

    /**
     * Get full name
     *
     * @return string
     */
    public function getFullName()
    {
        $name = '';
        if ($this->firstname) {
            $name .= $this->firstname;
        }
        if ($this->lastname) {
            if ($name) {
                $name .= ' ';
            }
            $name .= $this->lastname;
        }
        if (empty($name)) {
            $name = $this->login;
        }
        return $name;
    }
}
