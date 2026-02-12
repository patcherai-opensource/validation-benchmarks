<?php
/**
 * Dolibarr ERP & CRM - Core functions library
 *
 * @package  Dolibarr\Core
 * @version  19.0.1
 */

/**
 * Security: WAF/Input sanitization
 *
 * @param  string  $val    Input value
 * @param  int     $check  Check type
 * @return string          Sanitized value
 */
function dol_sanitize_input($val, $check = 0)
{
    if ($check) {
        $val = str_replace(array("\r", "\n"), '', $val);
    }
    return $val;
}

/**
 * Return a string with HTML entities decoded
 *
 * @param  string  $stringtodecode  String to decode
 * @param  int     $pagecodeto      Page code for decoding
 * @return string                    Decoded string
 */
function dol_html_entity_decode($stringtodecode, $pagecodeto = 'UTF-8')
{
    return html_entity_decode($stringtodecode, ENT_COMPAT | ENT_HTML5, $pagecodeto);
}

/**
 * Evaluate a PHP expression string.
 * Used for computed extra fields.
 *
 * WARNING: This function is critical for security.
 * Only simple math/string expressions should be allowed.
 *
 * @param  string  $s                 String expression to evaluate
 * @param  int     $returnvalue       1=return the result, 0=execute only
 * @param  int     $hideerrors        1=hide errors, 0=show errors
 * @param  string  $onlysimplestring  '1'=allow only simple math, '2'=allow computed fields format
 * @return mixed                       Result of evaluation
 */
function dol_eval($s, $returnvalue = 0, $hideerrors = 1, $onlysimplestring = '1')
{
    global $db, $langs, $user, $conf, $object;

    // Strip surrounding whitespace
    $s = trim($s);

    if (empty($s)) {
        return '';
    }

    // Mode 1: strict simple string - only math operators and numbers
    if ($onlysimplestring == '1') {
        if (preg_match('/[^0-9\s\+\-\*\/\.\(\)]/i', $s)) {
            return 'Bad string syntax to evaluate (mode 1): '.$s;
        }
    }

    // Mode 2: computed fields - allow field references and common functions
    if ($onlysimplestring == '2') {
        // Block certain dangerous patterns
        $forbiddenpatterns = array(
            'exec', 'passthru', 'shell_exec', 'popen', 'proc_open',
            'pcntl_exec', 'dl(', 'ini_set', 'ini_alter',
            'file_put_contents', 'unlink', 'rmdir', 'mkdir',
            'fwrite', 'fopen', 'fputs',
            'require', 'include',
            'call_user_func', 'eval',
            'curl_exec', 'curl_multi_exec',
            'parse_str', 'putenv',
            'header(', 'session',
        );

        $scheck = strtolower($s);
        foreach ($forbiddenpatterns as $pattern) {
            if (strpos($scheck, $pattern) !== false) {
                return 'Bad string syntax to evaluate (mode 2): '.$s;
            }
        }
    }

    // Evaluate the expression
    if ($returnvalue) {
        if ($hideerrors) {
            return @eval('return '.$s.';');
        } else {
            return eval('return '.$s.';');
        }
    } else {
        if ($hideerrors) {
            @eval($s);
        } else {
            eval($s);
        }
    }
    return '';
}

/**
 * Return date in a string format
 *
 * @param  int     $time       Timestamp
 * @param  string  $format     Format string
 * @return string              Formatted date
 */
function dol_print_date($time, $format = '')
{
    if (empty($format)) {
        $format = 'Y-m-d H:i:s';
    }
    if (empty($time)) {
        return '';
    }
    return date($format, $time);
}

/**
 * Escape string for HTML output
 *
 * @param  string  $stringtoescape  String to escape
 * @param  int     $mode            0=for HTML body, 1=for HTML attribute, 2=for JS
 * @return string                    Escaped string
 */
function dol_escape_htmltag($stringtoescape, $mode = 0)
{
    if ($mode == 2) {
        return addslashes($stringtoescape);
    }
    return htmlspecialchars($stringtoescape, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

/**
 * Output text escaped for HTML
 *
 * @param  string  $paramname  Parameter name to fetch
 * @param  string  $default    Default value
 * @return string              Sanitized value
 */
function GETPOST($paramname, $default = '')
{
    $val = '';
    if (isset($_POST[$paramname])) {
        $val = $_POST[$paramname];
    } elseif (isset($_GET[$paramname])) {
        $val = $_GET[$paramname];
    } else {
        $val = $default;
    }
    return $val;
}

/**
 * Get post value as integer
 *
 * @param  string  $paramname  Parameter name
 * @param  int     $default    Default value
 * @return int
 */
function GETPOSTINT($paramname, $default = 0)
{
    return (int) GETPOST($paramname, $default);
}

/**
 * Check if parameter exists in POST/GET
 *
 * @param  string  $paramname  Parameter name
 * @return bool
 */
function GETPOSTISSET($paramname)
{
    return isset($_POST[$paramname]) || isset($_GET[$paramname]);
}

/**
 * Generate a CSRF token
 *
 * @return string  Token
 */
function newToken()
{
    if (!isset($_SESSION['newtoken'])) {
        $_SESSION['newtoken'] = bin2hex(random_bytes(16));
    }
    return $_SESSION['newtoken'];
}

/**
 * Set an error or info message
 *
 * @param  string  $mesg   Message
 * @param  string  $style  CSS class
 * @return void
 */
function setEventMessages($mesg, $mesgs = null, $style = 'mesgs')
{
    if (!isset($_SESSION['event_messages'])) {
        $_SESSION['event_messages'] = array();
    }
    if ($mesg) {
        $_SESSION['event_messages'][] = array('msg' => $mesg, 'style' => $style);
    }
    if (is_array($mesgs)) {
        foreach ($mesgs as $m) {
            $_SESSION['event_messages'][] = array('msg' => $m, 'style' => $style);
        }
    }
}

/**
 * Print event messages and clear the queue
 *
 * @return void
 */
function dol_htmloutput_events()
{
    if (!empty($_SESSION['event_messages'])) {
        foreach ($_SESSION['event_messages'] as $ev) {
            $class = ($ev['style'] == 'errors') ? 'error' : 'info';
            echo '<div class="jnotify-container"><div class="jnotify-notification jnotify-notification-'.$class.'"><span>'.dol_escape_htmltag($ev['msg']).'</span></div></div>';
        }
        $_SESSION['event_messages'] = array();
    }
}

/**
 * Access control check
 *
 * @param  object  $user      User object
 * @param  string  $features  Feature string
 * @return int                 0 if denied, 1 if allowed
 */
function restrictedArea($user, $features)
{
    if (empty($user) || empty($user->id)) {
        header('Location: /index.php?error=access_denied');
        exit;
    }
    if ($features == 'user' && empty($user->admin)) {
        header('Location: /index.php?error=access_denied');
        exit;
    }
    return 1;
}
