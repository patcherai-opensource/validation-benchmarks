<?php
namespace TeamPass\Api\Controller;

class FolderController
{
    public function getFolders($request)
    {
        $userId = $request->getAttribute('user_id');
        // Return folders accessible to user
        return $this->jsonResponse(['folders' => []]);
    }

    private function jsonResponse($data, $code = 200)
    {
        http_response_code($code);
        header('Content-Type: application/json');
        echo json_encode($data);
    }
}
