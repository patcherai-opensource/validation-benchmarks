const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 8333;
const STATIC_DIR = './static';

// Faulty decode function - does NOT decode %2F to /
// This mimics the Oak framework vulnerability where decodeURIComponent was not used properly
function decodeComponent(input) {
    try {
        // Only decode safe characters, NOT slashes - this is the vulnerability!
        // This partial decoding allows path traversal via %2F
        return input.replace(/%(?!2[fF])([0-9A-Fa-f]{2})/g, (match, hex) => {
            return String.fromCharCode(parseInt(hex, 16));
        });
    } catch {
        return input;
    }
}

// Faulty isHidden check - only checks the first segment
// This is the second part of the vulnerability from the CVE
function isHidden(filePath) {
    const segments = filePath.split('/').filter(s => s.length > 0);
    // BUG: Only checks first segment, allowing bypass via /valid%2f../.hidden
    if (segments.length > 0 && segments[0].startsWith('.')) {
        return true;
    }
    return false;
}

const server = http.createServer((req, res) => {
    let urlPath = req.url || '/';
    
    // Remove query string
    urlPath = urlPath.split('?')[0];
    
    // Decode using our faulty decoder (doesn't decode %2F)
    let decodedPath = decodeComponent(urlPath);
    
    // Check if path is "hidden" using our faulty check
    if (isHidden(decodedPath)) {
        res.writeHead(403, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Access to hidden files is forbidden', code: 403 }));
        return;
    }
    
    // Now do full decode for actual file resolution (this is where the vuln manifests)
    // The attacker can use /valid%2f../.env - the isHidden check sees "valid" as first segment
    // but the actual path resolves to ../.env after full decode
    const fullDecodedPath = decodeURIComponent(urlPath);
    
    // Resolve the file path
    const filePath = path.join(STATIC_DIR, fullDecodedPath);
    
    // Directory listing for root
    if (fullDecodedPath === '/' || fullDecodedPath === '') {
        try {
            const files = fs.readdirSync(STATIC_DIR).filter(f => !f.startsWith('.'));
            res.writeHead(200, { 'Content-Type': 'text/html' });
            res.end(`<!DOCTYPE html>
<html>
<head><title>ArtVault CDN - Content Delivery</title></head>
<body style="font-family: Arial, sans-serif; padding: 20px; background: #1a1a1a; color: #fff;">
<h1>ArtVault CDN</h1>
<p>Static content delivery service for ArtVault platform.</p>
<h2>Available directories:</h2>
<ul>
${files.map(f => {
    const stat = fs.statSync(path.join(STATIC_DIR, f));
    return stat.isDirectory() ? `<li><a href="/${f}/" style="color: #4fc3f7;">${f}/</a></li>` : '';
}).join('\n')}
</ul>
<p style="color: #888; margin-top: 40px;">ArtVault CDN v2.1.3</p>
</body>
</html>`);
        } catch (err) {
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'Internal server error' }));
        }
        return;
    }
    
    // Check if it's a directory
    if (fs.existsSync(filePath) && fs.statSync(filePath).isDirectory()) {
        try {
            const files = fs.readdirSync(filePath).filter(f => !f.startsWith('.'));
            res.writeHead(200, { 'Content-Type': 'text/html' });
            res.end(`<!DOCTYPE html>
<html>
<head><title>ArtVault CDN - ${fullDecodedPath}</title></head>
<body style="font-family: Arial, sans-serif; padding: 20px; background: #1a1a1a; color: #fff;">
<h1>ArtVault CDN</h1>
<p>Directory: ${fullDecodedPath}</p>
<h2>Contents:</h2>
<ul>
<li><a href="../" style="color: #4fc3f7;">..</a></li>
${files.map(f => {
    const fPath = path.join(filePath, f);
    const stat = fs.statSync(fPath);
    return stat.isDirectory() 
        ? `<li><a href="${f}/" style="color: #4fc3f7;">${f}/</a></li>` 
        : `<li><a href="${f}" style="color: #81c784;">${f}</a></li>`;
}).join('\n')}
</ul>
</body>
</html>`);
        } catch (err) {
            res.writeHead(404, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'Directory not found' }));
        }
        return;
    }
    
    // Serve file
    fs.readFile(filePath, (err, data) => {
        if (err) {
            if (err.code === 'ENOENT') {
                res.writeHead(404, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'File not found', path: fullDecodedPath }));
            } else {
                res.writeHead(500, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'Internal server error' }));
            }
            return;
        }
        
        // Determine content type
        const ext = path.extname(filePath).toLowerCase();
        const mimeTypes = {
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
        
        const contentType = mimeTypes[ext] || 'application/octet-stream';
        res.writeHead(200, { 'Content-Type': contentType });
        res.end(data);
    });
});

server.listen(PORT, '0.0.0.0', () => {
    console.log(`ArtVault CDN server listening on port ${PORT}`);
});
