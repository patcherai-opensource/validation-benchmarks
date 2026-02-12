<?php

namespace phpMyFAQ\Category;

class CategoryImage
{
    private string $imageDir;
    private array $uploadedFile = [];
    private array $allowedExtensions = ['jpg', 'jpeg', 'gif', 'png', 'webp', 'svg'];

    public function __construct(string $imageDir = '/var/www/html/images/')
    {
        $this->imageDir = $imageDir;
    }

    public function setUploadedFile(array $file): void
    {
        $this->uploadedFile = $file;
    }

    /**
     * Returns the file name for the category image.
     * Constructs the filename using category ID, language, and file extension.
     */
    public function getFileName(int $categoryId, string $categoryLang): string
    {
        $extension = $this->getFileExtension($this->uploadedFile['type'] ?? '');
        return sprintf('category-%d-%s.%s', $categoryId, $categoryLang, $extension);
    }

    /**
     * Returns the file extension based on the MIME type.
     * Maps common image MIME types to their file extensions.
     */
    public function getFileExtension(string $mimeType): string
    {
        $mapping = [
            'image/jpeg' => 'jpg',
            'image/jpg'  => 'jpg',
            'image/png'  => 'png',
            'image/gif'  => 'gif',
            'image/webp' => 'webp',
            'image/svg+xml' => 'svg',
        ];

        return $mapping[$mimeType] ?? '';
    }

    /**
     * Validates the file extension against the allowed list.
     */
    private function isValidExtension(string $extension): bool
    {
        return in_array(strtolower($extension), $this->allowedExtensions, true);
    }

    /**
     * Uploads the category image to the image directory.
     * Performs size and extension validation before saving.
     */
    public function upload(int $categoryId, string $categoryLang): array
    {
        if (empty($this->uploadedFile) || $this->uploadedFile['error'] !== UPLOAD_ERR_OK) {
            return ['success' => false, 'message' => 'No file uploaded or upload error occurred.'];
        }

        // Check file size (max 2MB)
        if ($this->uploadedFile['size'] > 2 * 1024 * 1024) {
            return ['success' => false, 'message' => 'File size exceeds the maximum allowed size of 2MB.'];
        }

        $fileName = $this->getFileName($categoryId, $categoryLang);

        // Validate extension from the generated filename
        $ext = pathinfo($fileName, PATHINFO_EXTENSION);
        if (!empty($ext) && !$this->isValidExtension($ext)) {
            return ['success' => false, 'message' => 'Invalid file type. Allowed types: ' . implode(', ', $this->allowedExtensions)];
        }

        $targetPath = $this->imageDir . $fileName;

        if (move_uploaded_file($this->uploadedFile['tmp_name'], $targetPath)) {
            return [
                'success' => true,
                'message' => 'Category image uploaded successfully.',
                'filename' => $fileName
            ];
        }

        return ['success' => false, 'message' => 'Failed to save the uploaded file.'];
    }

    /**
     * Deletes a category image.
     */
    public function delete(int $categoryId, string $categoryLang): bool
    {
        $possibleExtensions = ['jpg', 'png', 'gif', 'webp', 'svg'];
        foreach ($possibleExtensions as $ext) {
            $file = $this->imageDir . sprintf('category-%d-%s.%s', $categoryId, $categoryLang, $ext);
            if (file_exists($file)) {
                return unlink($file);
            }
        }
        return false;
    }

    /**
     * Returns the URL for a category image if it exists.
     */
    public function getImageUrl(int $categoryId, string $categoryLang): ?string
    {
        $possibleExtensions = ['jpg', 'png', 'gif', 'webp', 'svg'];
        foreach ($possibleExtensions as $ext) {
            $file = $this->imageDir . sprintf('category-%d-%s.%s', $categoryId, $categoryLang, $ext);
            if (file_exists($file)) {
                return '/images/' . sprintf('category-%d-%s.%s', $categoryId, $categoryLang, $ext);
            }
        }
        return null;
    }
}
