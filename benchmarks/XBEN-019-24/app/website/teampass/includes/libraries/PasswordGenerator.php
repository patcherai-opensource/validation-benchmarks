<?php
namespace TeamPass\Libraries;

class PasswordGenerator
{
    private $length;
    private $useUppercase = true;
    private $useLowercase = true;
    private $useNumbers = true;
    private $useSymbols = true;

    public function __construct($length = 16)
    {
        $this->length = $length;
    }

    public function generate()
    {
        $chars = '';
        if ($this->useLowercase) $chars .= 'abcdefghijklmnopqrstuvwxyz';
        if ($this->useUppercase) $chars .= 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
        if ($this->useNumbers) $chars .= '0123456789';
        if ($this->useSymbols) $chars .= '!@#$%^&*()_+-=[]{}|;:,.<>?';

        $password = '';
        $max = strlen($chars) - 1;
        for ($i = 0; $i < $this->length; $i++) {
            $password .= $chars[random_int(0, $max)];
        }
        return $password;
    }
}
