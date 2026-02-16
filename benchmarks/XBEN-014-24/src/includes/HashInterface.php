<?php

interface HashInterface
{
    public function verifyPassword($plaintext, $storedHash);
    public function createHash($password, $salt = null);
    public function getSaltLength();
    public function isAvailable();
    public function isUpdateNeeded($hash);
    public function isValidHash($hash);
    public function getPrefix();
}
