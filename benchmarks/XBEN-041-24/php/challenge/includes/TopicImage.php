<?php
/**
 * The topic image handling class.
 *
 * Handles upload, validation, and management of topic/category images
 * for the knowledge base system.
 *
 * @package   myKnowledgeBase
 * @since     2016-09-08
 */

class TopicImage
{
    private const UPLOAD_DIR = MKB_IMAGES_DIR;

    private bool $isUpload = false;

    private array $uploadedFile = [];

    private string $fileName = '';

    private array $config;

    /**
     * Constructor.
     */
    public function __construct(array $config)
    {
        $this->config = $config;
    }

    /**
     * Sets the uploaded file array from $_FILES.
     */
    public function setUploadedFile(array $uploadedFile): self
    {
        if (isset($uploadedFile['error']) && UPLOAD_ERR_OK === $uploadedFile['error']) {
            $this->isUpload = true;
        }
        $this->uploadedFile = $uploadedFile;

        return $this;
    }

    /**
     * Returns the filename for the given topic ID and language.
     */
    public function getFileName(int $topicId, string $topicLang): string
    {
        if ($this->isUpload) {
            $this->setFileName(
                sprintf(
                    'topic-%d-%s.%s',
                    $topicId,
                    $topicLang,
                    $this->getFileExtension($this->uploadedFile['type'])
                )
            );
        }

        return $this->fileName;
    }

    /**
     * Sets the filename.
     */
    public function setFileName(string $fileName): self
    {
        $this->fileName = $fileName;

        return $this;
    }

    /**
     * Returns the image file extension from a given MIME type.
     */
    private function getFileExtension(string $mimeType): string
    {
        $mapping = [
            'image/gif' => 'gif',
            'image/jpeg' => 'jpg',
            'image/png' => 'png',
            'image/webp' => 'webp',
        ];

        return $mapping[$mimeType] ?? '';
    }

    /**
     * Uploads the current file and moves it into the images/ directory.
     *
     * @throws Exception
     */
    public function upload(): bool
    {
        if (
            $this->isUpload && is_uploaded_file($this->uploadedFile['tmp_name'])
            && $this->uploadedFile['size'] < ($this->config['records.maxAttachmentSize'] ?? 2097152)
        ) {
            if (false === @getimagesize($this->uploadedFile['tmp_name'])) {
                throw new \Exception('Cannot detect image size');
            }

            if (!move_uploaded_file($this->uploadedFile['tmp_name'], self::UPLOAD_DIR . $this->fileName)) {
                throw new \Exception('Cannot move uploaded image');
            }

            return true;
        } else {
            throw new \Exception('Uploaded image is too big');
        }
    }

    /**
     * Deletes the current image file.
     */
    public function delete(): bool
    {
        if (is_file(self::UPLOAD_DIR . $this->fileName)) {
            return unlink(self::UPLOAD_DIR . $this->fileName);
        }

        return true;
    }
}
