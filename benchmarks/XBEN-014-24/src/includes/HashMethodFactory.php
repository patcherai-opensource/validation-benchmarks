<?php

class HashMethodFactory
{
    protected static $instance = null;

    protected static $registeredMethods = [
        'StandardHashMethod' => 'StandardHashMethod',
        'EnhancedHashMethod' => 'EnhancedHashMethod',
    ];

    public static function getRegisteredMethods()
    {
        return self::$registeredMethods;
    }

    public static function resolveInstance($storedHash = '', $defaultMethod = 'StandardHashMethod')
    {
        if (!is_object(self::$instance) || !empty($storedHash) || $storedHash === null) {
            if (!empty($storedHash)) {
                $found = self::detectMethod($storedHash, $defaultMethod);
                if (!$found) {
                    self::$instance = null;
                }
            } else {
                $className = $defaultMethod;
                if (class_exists($className)) {
                    self::$instance = new $className();
                }
            }
        }
        return self::$instance;
    }

    protected static function detectMethod($storedHash, $defaultMethod)
    {
        $methods = self::$registeredMethods;
        $defaultRef = isset($methods[$defaultMethod]) ? $methods[$defaultMethod] : null;
        if ($defaultRef) {
            unset($methods[$defaultMethod]);
            $methods = [$defaultMethod => $defaultRef] + $methods;
        }

        $found = false;
        foreach ($methods as $methodClass) {
            if (class_exists($methodClass)) {
                $obj = new $methodClass();
                if ($obj instanceof HashInterface && $obj->isValidHash($storedHash)) {
                    self::$instance = $obj;
                    $found = true;
                    break;
                }
            }
        }
        return $found;
    }

    public static function reset()
    {
        self::$instance = null;
    }
}
