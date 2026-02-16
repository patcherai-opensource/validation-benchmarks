<?php

class UserRepository
{
    protected $config;
    protected $db = null;

    public function __construct($config)
    {
        $this->config = $config;
    }

    protected function getConnection()
    {
        if ($this->db === null) {
            $dsn = sprintf(
                'mysql:host=%s;port=%d;dbname=%s;charset=utf8mb4',
                $this->config['db']['host'],
                $this->config['db']['port'],
                $this->config['db']['name']
            );
            $this->db = new PDO($dsn, $this->config['db']['user'], $this->config['db']['password'], [
                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            ]);
        }
        return $this->db;
    }

    public function findByUsername($username)
    {
        try {
            $stmt = $this->getConnection()->prepare(
                'SELECT id, username, password, legacy_hash, role, is_active FROM cms_users WHERE username = :username AND is_active = 1 LIMIT 1'
            );
            $stmt->execute(['username' => $username]);
            return $stmt->fetch();
        } catch (PDOException $e) {
            return null;
        }
    }

    public function getAllUsers()
    {
        try {
            $stmt = $this->getConnection()->query(
                'SELECT id, username, role, is_active, created_at FROM cms_users ORDER BY id'
            );
            return $stmt->fetchAll();
        } catch (PDOException $e) {
            return [];
        }
    }
}
