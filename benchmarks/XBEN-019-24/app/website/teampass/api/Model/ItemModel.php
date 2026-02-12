<?php
namespace TeamPass\Api\Model;

class ItemModel
{
    private $db;

    public function __construct()
    {
        $this->db = DatabaseConnection::getInstance();
    }

    public function getByFolder($folderId)
    {
        $stmt = $this->db->prepare(
            "SELECT i.id, i.label, i.description, i.id_tree 
             FROM teampass_items AS i 
             WHERE i.id_tree = ? AND i.inactif = 0"
        );
        $stmt->execute([$folderId]);
        return $stmt->fetchAll(\PDO::FETCH_ASSOC);
    }

    public function search($query)
    {
        $stmt = $this->db->prepare(
            "SELECT i.id, i.label, i.description 
             FROM teampass_items AS i 
             WHERE i.label LIKE ? AND i.inactif = 0"
        );
        $stmt->execute(["%{$query}%"]);
        return $stmt->fetchAll(\PDO::FETCH_ASSOC);
    }
}
