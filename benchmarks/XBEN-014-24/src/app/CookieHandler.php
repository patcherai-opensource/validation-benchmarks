<?php

namespace App;

class CookieHandler
{
    /**
     * The encrypter instance.
     *
     * @var \App\AppEncrypter
     */
    protected $encrypter;

    /**
     * The names of the cookies that should not be encrypted.
     *
     * @var array
     */
    protected $excluded = [];

    /**
     * Create a new CookieHandler instance.
     *
     * @param  \App\AppEncrypter  $encrypter
     * @return void
     */
    public function __construct(AppEncrypter $encrypter)
    {
        $this->encrypter = $encrypter;
    }

    /**
     * Disable encryption for the given cookie name(s).
     *
     * @param  string|array  $name
     * @return void
     */
    public function exclude($name)
    {
        $this->excluded = array_merge($this->excluded, (array) $name);
    }

    /**
     * Decrypt all incoming cookies.
     *
     * @return array
     */
    public function processIncoming()
    {
        $decrypted = [];

        foreach ($_COOKIE as $key => $value) {
            if ($this->isExcluded($key)) {
                $decrypted[$key] = $value;
                continue;
            }

            try {
                $decrypted[$key] = $this->decryptValue($value);
            } catch (\Exception $e) {
                $decrypted[$key] = null;
            }
        }

        return $decrypted;
    }

    /**
     * Decrypt the given cookie value.
     *
     * @param  string|array  $value
     * @return mixed
     */
    protected function decryptValue($value)
    {
        if (is_array($value)) {
            return $this->decryptArrayValue($value);
        }

        return $this->encrypter->unsecure($value);
    }

    /**
     * Decrypt an array based cookie.
     *
     * @param  array  $values
     * @return array
     */
    protected function decryptArrayValue(array $values)
    {
        $decrypted = [];

        foreach ($values as $key => $value) {
            if (is_string($value)) {
                $decrypted[$key] = $this->encrypter->unsecure($value);
            }
        }

        return $decrypted;
    }

    /**
     * Create an encrypted cookie value for setting.
     *
     * @param  string  $name
     * @param  mixed   $value
     * @param  int     $expire
     * @param  string  $path
     * @return void
     */
    public function setEncrypted($name, $value, $expire = 0, $path = '/')
    {
        $encrypted = $this->encrypter->secure($value);
        setcookie($name, $encrypted, $expire, $path);
    }

    /**
     * Determine whether encryption has been disabled for the given cookie.
     *
     * @param  string $name
     * @return bool
     */
    public function isExcluded($name)
    {
        return in_array($name, $this->excluded);
    }
}
