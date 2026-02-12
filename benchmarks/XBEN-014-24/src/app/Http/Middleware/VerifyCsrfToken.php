<?php

namespace App\Http\Middleware;

use App\Encryption\Encrypter;

class VerifyCsrfToken
{
    protected $encrypter;
    protected $except = [];

    public function __construct(Encrypter $encrypter)
    {
        $this->encrypter = $encrypter;
    }

    public function handle($request)
    {
        if ($this->isReading($request) || $this->inExceptArray($request) || $this->tokensMatch($request)) {
            return true;
        }

        return false;
    }

    protected function isReading($request)
    {
        return in_array($request['method'], ['HEAD', 'GET', 'OPTIONS']);
    }

    protected function inExceptArray($request)
    {
        foreach ($this->except as $except) {
            if ($request['uri'] === $except) {
                return true;
            }
        }
        return false;
    }

    protected function tokensMatch($request)
    {
        $token = $this->getTokenFromRequest($request);
        $sessionToken = isset($request['session']['_token']) ? $request['session']['_token'] : null;

        return is_string($sessionToken) &&
               is_string($token) &&
               hash_equals($sessionToken, $token);
    }

    protected function getTokenFromRequest($request)
    {
        $token = isset($request['post']['_token']) ? $request['post']['_token'] : null;

        if (!$token && isset($request['headers']['X-CSRF-TOKEN'])) {
            $token = $request['headers']['X-CSRF-TOKEN'];
        }

        if (!$token && isset($request['headers']['X-XSRF-TOKEN'])) {
            $header = $request['headers']['X-XSRF-TOKEN'];
            $token = $this->encrypter->decrypt($header);
        }

        return $token;
    }

    public function addCookieToResponse($response, $token)
    {
        $encrypted = $this->encrypter->encrypt($token);
        return $encrypted;
    }
}