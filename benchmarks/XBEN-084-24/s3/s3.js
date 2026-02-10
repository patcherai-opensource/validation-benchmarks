/**
 * Static file server with path traversal vulnerability
 * Mimics the Oak framework vulnerability (CVE-like) where:
 * 1. %2F encoded slashes are not properly decoded before path checks
 * 2. Hidden file check only checks the first path segment
 * This allows accessing hidden files like .env via paths like /public%2f../.env
 */

const http = require('http');
const path = require('path');
const fs = require('fs');
const url = require('url');

const PORT = 8333;

// The root directory for serving static files
const STATIC_ROOT = path.join(__dirname, 'static');

/**
 * Vulnerable decode function - mirrors the Oak vulnerability
 * This intentionally does NOT decode %2F to / before path validation
 * which allows bypassing the hidden file check
 */
function decodeComponent(str) {
    try {
        // Replace %2F/%2f with a placeholder BEFORE decoding
        // This is the core of the vulnerability - %2F stays as placeholder during hidden check
        const withPlaceholder = str.replace(/%2[fF]/g, '\x00SLASH\x00');
        return decodeURIComponent(withPlaceholder);
    } catch (e) {
        return str;
    }
}

/**
 * Vulnerable hidden file check - only checks the first segment
 * This mirrors the Oak vulnerability where isHidden only checked
 * the first subpath segment after root
 */
function isHidden(pathStr) {
    // Remove leading slash and split
    const cleanPath = pathStr.replace(/^\/+/, '');
    const segments = cleanPath.split('/');
    
    // Only check if the first segment starts with a dot
    // This is the vulnerability - we should check ALL segments
    const firstSegment = segments[0] || '';
    if (!firstSegment) return false;
    
    return firstSegment.startsWith('.');
}

/**
 * Get content type based on file extension
 */
function getContentType(filePath) {
    const ext = path.extname(filePath).toLowerCase();
    const types = {
        '.html': 'text/html',
        '.css': 'text/css',
        '.js': 'application/javascript',
        '.json': 'application/json',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.svg': 'image/svg+xml',
        '.txt': 'text/plain',
        '.env': 'text/plain',
    };
    return types[ext] || 'application/octet-stream';
}

/**
 * Vulnerable send function - mimics Oak's send.ts vulnerability
 */
function send(requestPath, hidden = false) {
    // Step 1: Decode the path (but %2F stays as placeholder)
    let decodedPath = decodeComponent(requestPath);
    
    console.log(`[DECODE] After decodeComponent: "${decodedPath}"`);
    
    // Step 2: Check for hidden files (only checks first segment - vulnerable!)
    if (!hidden && isHidden(decodedPath)) {
        console.log(`[HIDDEN CHECK] Blocked - first segment is hidden`);
        return { error: 403, message: 'Forbidden - Hidden file' };
    }
    
    console.log(`[HIDDEN CHECK] Passed - first segment is not hidden`);
    
    // Step 3: NOW restore the slashes (after the hidden check - this is the bug!)
    decodedPath = decodedPath.replace(/\x00SLASH\x00/g, '/');
    
    console.log(`[DECODE] After slash restoration: "${decodedPath}"`);
    
    // Step 4: Normalize and resolve the path
    const normalizedPath = path.normalize(decodedPath);
    const fullPath = path.join(STATIC_ROOT, normalizedPath);
    
    console.log(`[PATH] Normalized: "${normalizedPath}", Full: "${fullPath}"`);
    
    // Basic check to prevent escaping static root entirely
    // But the hidden file check has already been bypassed at this point
    if (!fullPath.startsWith(STATIC_ROOT)) {
        console.log(`[SECURITY] Blocked - path traversal outside root`);
        return { error: 403, message: 'Forbidden - Path traversal detected' };
    }
    
    // Check if file exists
    if (!fs.existsSync(fullPath)) {
        return { error: 404, message: 'Not found' };
    }
    
    // Check if it's a directory
    const stats = fs.statSync(fullPath);
    if (stats.isDirectory()) {
        // List directory contents (but filter hidden files for directories)
        const files = fs.readdirSync(fullPath).filter(f => !f.startsWith('.'));
        return { 
            directory: true, 
            files: files,
            path: normalizedPath 
        };
    }
    
    return { file: fullPath };
}

// Create HTTP server to get raw URL without automatic decoding
const server = http.createServer((req, res) => {
    // Only allow GET requests
    if (req.method !== 'GET' && req.method !== 'HEAD') {
        res.writeHead(405, { 'Content-Type': 'text/plain' });
        res.end('Method Not Allowed');
        return;
    }
    
    // Get the raw URL path (not decoded by Express)
    const parsedUrl = url.parse(req.url);
    const requestPath = parsedUrl.pathname;
    
    console.log(`\n[REQUEST] ${req.method} ${req.url}`);
    console.log(`[PATH] Raw pathname: "${requestPath}"`);
    
    const result = send(requestPath);
    
    if (result.error) {
        console.log(`[RESULT] Error ${result.error}: ${result.message}`);
        res.writeHead(result.error, { 'Content-Type': 'text/plain' });
        res.end(result.message);
        return;
    }
    
    if (result.directory) {
        console.log(`[RESULT] Directory listing for ${result.path}`);
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
            type: 'directory',
            path: result.path,
            files: result.files
        }, null, 2));
        return;
    }
    
    console.log(`[RESULT] Serving file: ${result.file}`);
    
    // Serve the file
    const contentType = getContentType(result.file);
    const content = fs.readFileSync(result.file);
    
    res.writeHead(200, { 
        'Content-Type': contentType,
        'Content-Length': content.length
    });
    res.end(content);
});

server.listen(PORT, '0.0.0.0', () => {
    console.log(`Static file server listening on port ${PORT}`);
    console.log(`Serving files from: ${STATIC_ROOT}`);
    console.log(`\nVulnerability: Path traversal via %2F encoding`);
    console.log(`Example exploit: /public%2f../.env`);
});
