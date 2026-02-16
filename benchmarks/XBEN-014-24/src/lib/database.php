<?php
/**
 * Database connection manager for SecurePortal
 * Uses SQLite for simplicity in containerized deployments
 */

function getDatabaseConnection(): PDO
{
    $dbPath = '/var/www/data/portal.db';

    $db = new PDO('sqlite:' . $dbPath);
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $db->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);

    return $db;
}
