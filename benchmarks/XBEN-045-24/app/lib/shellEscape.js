/**
 * Shell argument escaping library for secure command execution
 * Handles escaping of special characters for shell commands
 */

const escapeShellArg = (arg, options = {}) => {
    if (typeof arg !== 'string') {
        arg = String(arg);
    }

    const shell = options.shell || 'sh';
    
    if (shell === 'cmd' || shell === 'cmd.exe') {
        return escapeArgCmd(arg);
    }
    
    return escapeArgUnix(arg);
};

const escapeArgUnix = (arg) => {
    if (arg === '') {
        return "''";
    }
    
    let result = arg.replace(/\x00/g, '');
    
    result = result
        .replace(/'/g, "'\"'\"'")
        .replace(/"/g, '\\"')
        .replace(/\$/g, '\\$')
        .replace(/`/g, '\\`')
        .replace(/!/g, '\\!')
        .replace(/\\/g, '\\\\')
        .replace(/;/g, '\\;')
        .replace(/&/g, '\\&')
        .replace(/\|/g, '\\|')
        .replace(/</g, '\\<')
        .replace(/>/g, '\\>')
        .replace(/\(/g, '\\(')
        .replace(/\)/g, '\\)')
        .replace(/\[/g, '\\[')
        .replace(/\]/g, '\\]')
        .replace(/\{/g, '\\{')
        .replace(/\}/g, '\\}')
        .replace(/#/g, '\\#')
        .replace(/\*/g, '\\*')
        .replace(/\?/g, '\\?')
        .replace(/~/g, '\\~')
        .replace(/\^/g, '\\^');
    
    return result;
};

const escapeArgCmd = (arg) => {
    if (arg === '') {
        return '""';
    }
    
    let result = arg.replace(/\x00/g, '');
    
    result = result.replace(/(["%^&<>|])/g, '^$1');
    
    if (/\s/.test(result)) {
        result = '"' + result + '"';
    }
    
    return result;
};

const quote = (arg, options = {}) => {
    const escaped = escapeShellArg(arg, options);
    const shell = options.shell || 'sh';
    
    if (shell === 'cmd' || shell === 'cmd.exe') {
        return '"' + escaped.replace(/"/g, '""') + '"';
    }
    
    return "'" + escaped.replace(/'/g, "'\\''") + "'";
};

const escapeAll = (args, options = {}) => {
    if (!Array.isArray(args)) {
        throw new TypeError('Expected an array of arguments');
    }
    return args.map(arg => escapeShellArg(arg, options));
};

const quoteAll = (args, options = {}) => {
    if (!Array.isArray(args)) {
        throw new TypeError('Expected an array of arguments');
    }
    return args.map(arg => quote(arg, options));
};

module.exports = {
    escape: escapeShellArg,
    quote,
    escapeAll,
    quoteAll
};
