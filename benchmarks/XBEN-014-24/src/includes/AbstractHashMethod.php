<?php

abstract class AbstractHashMethod implements HashInterface
{
    abstract protected function getSettingPrefix();
    abstract protected function generateSalt();

    public function getPrefix()
    {
        return $this->getSettingPrefix();
    }

    protected function getLengthBase64FromBytes($byteLength)
    {
        return (int)ceil($byteLength * 8 / 6);
    }
}
