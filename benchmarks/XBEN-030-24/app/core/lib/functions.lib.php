<?php
/**
 * Core library functions for GestiPro ERP
 * Includes formula evaluation, string processing, and utility functions
 */

/**
 * Sanitize and evaluate a formula string.
 * Used for computed extra fields - evaluates stored formulas when rendering objects.
 *
 * @param string $s             The string/formula to evaluate
 * @param int    $returnvalue   1=return result of eval, 0=execute only
 * @param int    $hideerrors    1=hide errors during eval
 * @param string $safemode      Safety level: '1' = strict, '2' = extended (allows more complex expressions)
 * @return mixed                Result of the evaluation
 */
function gp_safe_compute($s, $returnvalue = 0, $hideerrors = 1, $safemode = '1')
{
    global $db, $conf, $current_user;
    global $targetobject;

    if (!in_array($safemode, array('0', '1', '2'))) {
        return "Invalid call to gp_safe_compute. Parameter safemode must be '0', '1' or '2'";
    }

    try {
        if ($safemode == '1') {
            $allowedchars = '^$_+-.*>&|=!?():"\',/@';
            if (preg_match('/[^a-z0-9\s'.preg_quote($allowedchars, '/').']/', $s)) {
                if ($returnvalue) {
                    return 'Syntax error in expression (invalid characters detected): '.$s;
                } else {
                    return '';
                }
            }
            $scheck = preg_replace('/->[a-zA-Z0-9_]+\(/', '->__METHOD__', $s);
            $scheck = preg_replace('/^\(/', '__PAREN__ ', $scheck);
            $scheck = preg_replace('/\s\(/', '__PAREN__ ', $scheck);
            $scheck = preg_replace('/^!?[a-zA-Z0-9_]+\(/', '__FUNC__', $scheck);
            $scheck = preg_replace('/\s!?[a-zA-Z0-9_]+\(/', '__FUNC__', $scheck);
            $scheck = preg_replace('/(\^|\')\(/', '__REGSTART__', $scheck);
            if (strpos($scheck, '(') !== false) {
                if ($returnvalue) {
                    return 'Syntax error in expression (unexpected function call pattern): '.$s;
                } else {
                    return '';
                }
            }
        } elseif ($safemode == '2') {
            $allowedchars = '^$_+-.*>&|=!?():"\',/@[]';
            if (preg_match('/[^a-z0-9\s'.preg_quote($allowedchars, '/').']/', $s)) {
                if ($returnvalue) {
                    return 'Syntax error in expression (invalid characters detected): '.$s;
                } else {
                    return '';
                }
            }
            $scheck = preg_replace('/->[a-zA-Z0-9_]+\(/', '->__METHOD__', $s);
            $scheck = preg_replace('/^\(/', '__PAREN__ ', $scheck);
            $scheck = preg_replace('/\s\(/', '__PAREN__ ', $scheck);
            $scheck = preg_replace('/^!?[a-zA-Z0-9_]+\(/', '__FUNC__', $scheck);
            $scheck = preg_replace('/\s!?[a-zA-Z0-9_]+\(/', '__FUNC__', $scheck);
            $scheck = preg_replace('/(\^|\')\(/', '__REGSTART__', $scheck);
            if (strpos($scheck, '(') !== false) {
                if ($returnvalue) {
                    return 'Syntax error in expression (unexpected function call pattern): '.$s;
                } else {
                    return '';
                }
            }
        }

        if (is_array($s) || $s === 'Array') {
            return 'Syntax error: value is Array';
        }
        if (strpos($s, '::') !== false) {
            if ($returnvalue) {
                return 'Syntax error (double colon is not allowed): '.$s;
            } else {
                return '';
            }
        }
        if (strpos($s, '`') !== false) {
            if ($returnvalue) {
                return 'Syntax error (backtick is not allowed): '.$s;
            } else {
                return '';
            }
        }
        if (preg_match('/[^0-9]+\.[^0-9]+/', $s)) {
            if ($returnvalue) {
                return 'Syntax error (dot character is not allowed outside numeric context): '.$s;
            } else {
                return '';
            }
        }

        $blocked_strings = array('$$');
        $blocked_strings = array_merge($blocked_strings, array('_ENV', '_SESSION', '_COOKIE', '_GET', '_POST', '_REQUEST'));

        $blocked_functions = array("exec", "passthru", "shell_exec", "system", "proc_open", "popen");
        $blocked_functions = array_merge($blocked_functions, array("gp_safe_compute", "run_cli"));
        $blocked_functions = array_merge($blocked_functions, array("base64_decode", "rawurldecode", "urldecode"));
        $blocked_functions = array_merge($blocked_functions, array("fopen", "file_put_contents", "fputs", "fwrite", "fpassthru", "require", "include", "mkdir", "rmdir", "symlink", "touch", "unlink", "umask"));
        $blocked_functions = array_merge($blocked_functions, array("get_defined_functions", "get_defined_vars", "get_defined_constants", "get_declared_classes"));
        $blocked_functions = array_merge($blocked_functions, array("function", "call_user_func"));
        $blocked_functions = array_merge($blocked_functions, array("eval", "create_function", "assert", "mb_ereg_replace"));

        $block_regex = 'global\s+\$|\b('.implode('|', $blocked_functions).')\b';

        do {
            $oldstring = $s;
            $s = str_ireplace($blocked_strings, '__blocked__', $s);
            $s = preg_replace('/'.$block_regex.'/i', '__blocked__', $s);
        } while ($oldstring != $s);

        if (strpos($s, '__blocked__') !== false) {
            if ($returnvalue) {
                return 'Expression contains blocked function or variable: '.$s;
            } else {
                return '';
            }
        }

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
    } catch (Error $e) {
        if ($returnvalue) {
            return 'Evaluation error: '.$e->getMessage();
        }
    }
    return '';
}

function gp_escape_html($str) {
    return htmlspecialchars($str ?? '', ENT_QUOTES, 'UTF-8');
}

function gp_get_post($key, $default = '') {
    return isset($_POST[$key]) ? $_POST[$key] : (isset($_GET[$key]) ? $_GET[$key] : $default);
}

function gp_redirect($url) {
    header('Location: ' . $url);
    exit;
}
