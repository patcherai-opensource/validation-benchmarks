<?php
/**
 * Database connection singleton for SilverStripe ORM
 */
class SS_Database {
    private static $instance = null;
    private $connection;

    private function __construct() {
        $dbPath = '/var/www/data/silverstripe.sqlite';
        $this->connection = new SQLite3($dbPath);
        $this->connection->busyTimeout(5000);
    }

    public static function getConn() {
        if (self::$instance === null) {
            self::$instance = new self();
        }
        return self::$instance->connection;
    }
}
?>