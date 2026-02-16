<?php
/**
 * Abstract base class for password hashing methods.
 * Provides common utility functions for salt generation and encoding.
 */
abstract class AbstractHashMethod
{
    /**
     * Base64 character mapping used by crypt()-compatible encoding.
     */
    const ITOA64 = './0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';

    /**
     * Encode raw bytes into crypt-compatible base64 representation.
     *
     * @param string $input Raw byte string
     * @param int $count Number of bytes to encode
     * @return string Encoded string
     */
    public function base64Encode($input, $count)
    {
        $output = '';
        $i = 0;
        $itoa64 = self::ITOA64;
        do {
            $value = ord($input[$i++]);
            $output .= $itoa64[$value & 0x3f];
            if ($i < $count) {
                $value |= ord($input[$i]) << 8;
            }
            $output .= $itoa64[($value >> 6) & 0x3f];
            if ($i++ >= $count) {
                break;
            }
            if ($i < $count) {
                $value |= ord($input[$i]) << 16;
            }
            $output .= $itoa64[($value >> 12) & 0x3f];
            if ($i++ >= $count) {
                break;
            }
            $output .= $itoa64[($value >> 18) & 0x3f];
        } while ($i < $count);
        return $output;
    }

    /**
     * Calculate required base64 length for a given byte length.
     *
     * @param int $byteLength Number of bytes
     * @return int Required number of base64 characters
     */
    protected function getBase64LengthForBytes($byteLength)
    {
        return (int)ceil($byteLength * 8 / 6);
    }
}
