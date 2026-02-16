<?php

namespace App;

class AppEncrypter
{
    /**
     * The encryption key.
     *
     * @var string
     */
    protected $key;

    /**
     * The algorithm used for encryption.
     *
     * @var string
     */
    protected $cipher;

    /**
     * Create a new encrypter instance.
     *
     * @param  string  $key
     * @param  string  $cipher
     * @return void
     *
     * @throws \RuntimeException
     */
    public function __construct($key, $cipher = 'AES-256-CBC')
    {
        $key = (string) $key;

        if (static::isSupported($key, $cipher)) {
            $this->key = $key;
            $this->cipher = $cipher;
        } else {
            throw new \RuntimeException('The only supported ciphers are AES-128-CBC and AES-256-CBC with the correct key lengths.');
        }
    }

    /**
     * Determine if the given key and cipher combination is valid.
     *
     * @param  string  $key
     * @param  string  $cipher
     * @return bool
     */
    public static function isSupported($key, $cipher)
    {
        $length = mb_strlen($key, '8bit');

        return ($cipher === 'AES-128-CBC' && $length === 16) ||
               ($cipher === 'AES-256-CBC' && $length === 32);
    }

    /**
     * Encrypt the given value.
     *
     * @param  mixed  $value
     * @param  bool  $serialize
     * @return string
     */
    public function secure($value, $serialize = true)
    {
        $iv = random_bytes(openssl_cipher_iv_length($this->cipher));

        $value = \openssl_encrypt(
            $serialize ? serialize($value) : $value,
            $this->cipher, $this->key, 0, $iv
        );

        if ($value === false) {
            throw new \RuntimeException('Could not encrypt the data.');
        }

        $mac = $this->computeHash($iv = base64_encode($iv), $value);

        $json = json_encode(compact('iv', 'value', 'mac'));

        if (json_last_error() !== JSON_ERROR_NONE) {
            throw new \RuntimeException('Could not encrypt the data.');
        }

        return base64_encode($json);
    }

    /**
     * Encrypt a string without serialization.
     *
     * @param  string  $value
     * @return string
     */
    public function secureString($value)
    {
        return $this->secure($value, false);
    }

    /**
     * Decrypt the given value.
     *
     * @param  mixed  $payload
     * @param  bool  $unserialize
     * @return mixed
     */
    public function unsecure($payload, $unserialize = true)
    {
        $payload = $this->extractJsonPayload($payload);

        $iv = base64_decode($payload['iv']);

        $decrypted = \openssl_decrypt(
            $payload['value'], $this->cipher, $this->key, 0, $iv
        );

        if ($decrypted === false) {
            throw new \RuntimeException('Could not decrypt the data.');
        }

        return $unserialize ? unserialize($decrypted) : $decrypted;
    }

    /**
     * Decrypt the given string without unserialization.
     *
     * @param  string  $payload
     * @return string
     */
    public function unsecureString($payload)
    {
        return $this->unsecure($payload, false);
    }

    /**
     * Create a MAC for the given value.
     *
     * @param  string  $iv
     * @param  mixed  $value
     * @return string
     */
    protected function computeHash($iv, $value)
    {
        return hash_hmac('sha256', $iv . $value, $this->key);
    }

    /**
     * Get the JSON array from the given payload.
     *
     * @param  string  $payload
     * @return array
     */
    protected function extractJsonPayload($payload)
    {
        $payload = json_decode(base64_decode($payload), true);

        if (! $this->isValidPayload($payload)) {
            throw new \RuntimeException('The payload is invalid.');
        }

        if (! $this->isValidMac($payload)) {
            throw new \RuntimeException('The MAC is invalid.');
        }

        return $payload;
    }

    /**
     * Verify that the encryption payload is valid.
     *
     * @param  mixed  $payload
     * @return bool
     */
    protected function isValidPayload($payload)
    {
        return is_array($payload) && isset($payload['iv'], $payload['value'], $payload['mac']) &&
               strlen(base64_decode($payload['iv'], true)) === openssl_cipher_iv_length($this->cipher);
    }

    /**
     * Determine if the MAC for the given payload is valid.
     *
     * @param  array  $payload
     * @return bool
     */
    protected function isValidMac(array $payload)
    {
        $bytes = random_bytes(16);
        $calculated = $this->derivePayloadMac($payload, $bytes);

        return hash_equals(
            hash_hmac('sha256', $payload['mac'], $bytes, true), $calculated
        );
    }

    /**
     * Calculate the hash of the given payload.
     *
     * @param  array  $payload
     * @param  string  $bytes
     * @return string
     */
    protected function derivePayloadMac($payload, $bytes)
    {
        return hash_hmac(
            'sha256', $this->computeHash($payload['iv'], $payload['value']), $bytes, true
        );
    }

    /**
     * Get the encryption key.
     *
     * @return string
     */
    public function getKey()
    {
        return $this->key;
    }
}
