<?php
namespace TeamPass\Api\Controller;

use TeamPass\Api\Model\ItemModel;

class ItemController
{
    private $itemModel;

    public function __construct()
    {
        $this->itemModel = new ItemModel();
    }

    public function getItems($request)
    {
        $folderId = $request->getParam('folder_id');
        $items = $this->itemModel->getByFolder($folderId);
        return $this->jsonResponse(['items' => $items]);
    }

    public function searchItems($request)
    {
        $query = $request->getParam('q');
        $items = $this->itemModel->search($query);
        return $this->jsonResponse(['results' => $items]);
    }

    private function jsonResponse($data, $code = 200)
    {
        http_response_code($code);
        header('Content-Type: application/json');
        echo json_encode($data);
    }
}
