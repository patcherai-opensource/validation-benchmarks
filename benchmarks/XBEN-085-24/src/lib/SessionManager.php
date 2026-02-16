<?php
/**
 * Session Management
 *
 * Handles user authentication sessions.
 *
 * @package  AppCore\Session
 * @license  BSD-3-Clause
 */

namespace AppCore\Session;

class SessionManager
{
    /**
     * Start or resume session
     */
    public static function init()
    {
        if (session_status() === PHP_SESSION_NONE) {
            session_start();
        }
    }

    /**
     * Check if the user is authenticated
     *
     * @return bool
     */
    public static function isAuthenticated()
    {
        self::init();
        return isset($_SESSION['user_authenticated']) && $_SESSION['user_authenticated'] === true;
    }

    /**
     * Set the session as authenticated
     *
     * @param string $username
     * @param string $role
     */
    public static function authenticate($username, $role = 'user')
    {
        self::init();
        $_SESSION['user_authenticated'] = true;
        $_SESSION['username'] = $username;
        $_SESSION['role'] = $role;
        $_SESSION['login_time'] = time();
    }

    /**
     * Get the current username
     *
     * @return string|null
     */
    public static function getUsername()
    {
        self::init();
        return isset($_SESSION['username']) ? $_SESSION['username'] : null;
    }

    /**
     * Get the current user role
     *
     * @return string|null
     */
    public static function getRole()
    {
        self::init();
        return isset($_SESSION['role']) ? $_SESSION['role'] : null;
    }

    /**
     * Destroy session
     */
    public static function destroy()
    {
        self::init();
        $_SESSION = array();
        if (ini_get("session.use_cookies")) {
            $params = session_get_cookie_params();
            setcookie(session_name(), '', time() - 42000,
                $params["path"], $params["domain"],
                $params["secure"], $params["httponly"]
            );
        }
        session_destroy();
    }
}
