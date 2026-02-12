<?php
namespace TeamPass\Libraries;

class Encryption
{
    private $key;
    private $cipher = 'aes-256-cbc';

    public function __construct($saltKey)
    {
        $this->key = hash('sha256', $saltKey, true);
    }

    public function encrypt($data)
    {
        $iv = openssl_random_pseudo_bytes(openssl_cipher_iv_length($this->cipher));
        $encrypted = openssl_encrypt($data, $this->cipher, $this->key, 0, $iv);
        return base64_encode($iv . '::' . $encrypted);
    }

    public function decrypt($data)
    {
        list($iv, $encrypted) = explode('::', base64_decode($data), 2);
        return openssl_decrypt($encrypted, $this->cipher, $this->key, 0, $iv);
    }
}
