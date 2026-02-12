<?php

namespace App\Http\Middleware;

use App\Encryption\Encrypter;

class EncryptCookies
{
    protected $encrypter;

    protected $except = [];

    public function __construct(Encrypter $encrypter)
    {
        $this->encrypter = $encrypter;
    }

    public function handle($cookies)
    {
        return $this->decrypt($cookies);
    }

    protected function decrypt($cookies)
    {
        $decrypted = [];

        foreach ($cookies as $key => $cookie) {
            if ($this->isDisabled($key)) {
                $decrypted[$key] = $cookie;
                continue;
            }

            try {
                $decrypted[$key] = $this->decryptCookie($cookie);
            } catch (\Exception $e) {
                $decrypted[$key] = null;
            }
        }

        return $decrypted;
    }

    protected function decryptCookie($cookie)
    {
        return is_array($cookie)
            ? $this->decryptArray($cookie)
            : $this->encrypter->decrypt($cookie);
    }

    protected function decryptArray(array $cookie)
    {
        $decrypted = [];

        foreach ($cookie as $key => $value) {
            if (is_string($value)) {
                $decrypted[$key] = $this->encrypter->decrypt($value);
            }
        }

        return $decrypted;
    }

    public function encrypt($name, $value)
    {
        return $this->encrypter->encrypt($value);
    }

    public function isDisabled($name)
    {
        return in_array($name, $this->except);
    }
}