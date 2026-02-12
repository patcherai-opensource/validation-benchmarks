<?php
/**
 * Database connection manager
 * Provides singleton database connection for the application.
 */

namespace Pimcore;

class Db
{
    private static $instance = null;

    public static function getConnection()
    {
        if (self::$instance === null) {
            $servername = getenv('DB_HOST') ?: ($_ENV['DB_HOST'] ?? '127.0.0.1');
            $username = getenv('DB_USER') ?: ($_ENV['DB_USER'] ?? 'challenge');
            $password = getenv('DB_PASSWORD') ?: ($_ENV['DB_PASSWORD'] ?? 'challenge');
            $dbname = getenv('DB_NAME') ?: ($_ENV['DB_NAME'] ?? 'challenge');

            self::$instance = new \mysqli($servername, $username, $password, $dbname);

            if (self::$instance->connect_error) {
                throw new \Exception('Database connection failed');
            }

            self::$instance->set_charset('utf8mb4');
        }

        return self::$instance;
    }

    public static function reset()
    {
        if (self::$instance !== null) {
            self::$instance->close();
            self::$instance = null;
        }
    }
}
