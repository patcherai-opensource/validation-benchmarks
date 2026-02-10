<?php

class CategoryImage
{
    private $uploadedFile = [];
    
    private const ALLOWED_EXTENSIONS = [
        'image/png' => '.png',
        'image/jpeg' => '.jpg',
        'image/jpg' => '.jpg',
        'image/gif' => '.gif'
    ];
    
    public function setUploadedFile(array $file): void
    {
        $this->uploadedFile = $file;
    }
    
    public function getFileName(int $categoryId, string $categoryLang): string
    {
        $extension = $this->getFileExtension($this->uploadedFile['type']);
        return sprintf('category-%d-%s%s', $categoryId, $categoryLang, $extension);
    }
    
    private function getFileExtension(string $mimeType): string
    {
        if (isset(self::ALLOWED_EXTENSIONS[$mimeType])) {
            return self::ALLOWED_EXTENSIONS[$mimeType];
        }
        
        return '';
    }
    
    public function upload(string $destination): bool
    {
        if (empty($this->uploadedFile)) {
            return false;
        }
        
        $tmpFile = $this->uploadedFile['tmp_name'];
        
        if (!file_exists($tmpFile)) {
            return false;
        }
        
        return move_uploaded_file($tmpFile, $destination);
    }
}
?>
