<?php
/**
 * IP-based Access Control Filter
 *
 * Provides IP address filtering for restricted areas of the application.
 * Uses the framework's request object to determine the client IP,
 * supporting reverse proxy configurations.
 *
 * @package    App\Middleware
 */

class IPFilter
{
    /**
     * Check if the client IP is in the allowed list
     *
     * @param object $request  The incoming request object
     * @param array  $allowedIPs  List of allowed IP addresses
     * @return bool
     */
    public static function isAllowed($request, array $allowedIPs): bool
    {
        $clientIP = $request->getIPAddress();

        foreach ($allowedIPs as $allowed) {
            if (self::ipInRange($clientIP, $allowed)) {
                return true;
            }
        }

        return false;
    }

    /**
     * Check if an IP is within a CIDR range or matches exactly
     *
     * @param string $ip
     * @param string $range  IP or CIDR notation
     * @return bool
     */
    private static function ipInRange(string $ip, string $range): bool
    {
        if (strpos($range, '/') === false) {
            return $ip === $range;
        }

        list($subnet, $bits) = explode('/', $range);
        $ipLong    = ip2long($ip);
        $subnetLong = ip2long($subnet);
        $mask      = -1 << (32 - (int)$bits);

        return ($ipLong & $mask) === ($subnetLong & $mask);
    }

    /**
     * Log access attempt for audit trail
     *
     * @param string $ip
     * @param string $resource
     * @param bool   $allowed
     */
    public static function logAccess(string $ip, string $resource, bool $allowed): void
    {
        $status = $allowed ? 'ALLOWED' : 'DENIED';
        $timestamp = date('Y-m-d H:i:s');
        error_log("[{$timestamp}] IP Filter: {$status} access to {$resource} from {$ip}");
    }
}
