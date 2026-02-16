<?php
/**
 * Response Handler
 */

class Response
{
    protected $statusCode = 200;
    protected $headers = [];

    public function setStatusCode(int $code): self
    {
        $this->statusCode = $code;
        http_response_code($code);
        return $this;
    }

    public function setHeader(string $name, string $value): self
    {
        $this->headers[$name] = $value;
        header("$name: $value");
        return $this;
    }

    public function json(array $data, int $status = 200): void
    {
        $this->setStatusCode($status);
        $this->setHeader('Content-Type', 'application/json');
        echo json_encode($data);
    }

    public function redirect(string $url, int $status = 302): void
    {
        $this->setStatusCode($status);
        header("Location: $url");
        exit;
    }
}
