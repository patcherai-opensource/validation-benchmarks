<?php
namespace TeamPass\Api\Model;

class UserModel
{
    private $db;

    public function __construct()
    {
        $this->db = DatabaseConnection::getInstance();
    }

    public function findByLogin($login)
    {
        $stmt = $this->db->prepare("SELECT * FROM teampass_users WHERE login = ?");
        $stmt->execute([$login]);
        return $stmt->fetch(\PDO::FETCH_ASSOC);
    }

    public function findById($id)
    {
        $stmt = $this->db->prepare("SELECT * FROM teampass_users WHERE id = ?");
        $stmt->execute([$id]);
        return $stmt->fetch(\PDO::FETCH_ASSOC);
    }

    public function updateLastConnection($userId)
    {
        $stmt = $this->db->prepare("UPDATE teampass_users SET last_connexion = ? WHERE id = ?");
        $stmt->execute([time(), $userId]);
    }
}
