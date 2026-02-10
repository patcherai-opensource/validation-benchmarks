/**
 * Vulnerable File Server
 * This server simulates the vulnerability in httpster (CVE-2020-36629)
 * 
 * The vulnerability exists because the server serves files without 
 * properly validating that the resolved path remains within the 
 * intended web root directory after path normalization.
 */

const express = require('express');
const fs = require('fs');
const path = require('path');
const serveIndex = require('serve-index');

const app = express();
const PORT = 80;

// The intended web root directory
const webRoot = '/app/public';

// Logging middleware
app.use((req, res, next) => {
    console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
    next();
});

/**
 * VULNERABLE CODE
 * This implementation mimics the vulnerable behavior in httpster where
 * fs.realpathSync is used but paths are not properly validated to ensure
 * they remain within the web root.
 * 
 * The vulnerability allows path traversal via URL paths with encoded dots
 * The key issue is that we manually decode the URL and then join paths,
 * bypassing Express's built-in path normalization protections.
 */
app.get('*', (req, res, next) => {
    try {
        // Get raw URL to handle encoded sequences
        let requestPath = req.url;
        
        // Remove query string if present
        const queryIndex = requestPath.indexOf('?');
        if (queryIndex !== -1) {
            requestPath = requestPath.substring(0, queryIndex);
        }
        
        // Decode URL encoding (this is vulnerable - decodes before path validation)
        // URL-encoded sequences like %2e%2e can bypass initial path checks
        requestPath = decodeURIComponent(requestPath);
        
        // Join with web root - path.join normalizes .. sequences
        // VULNERABLE: After decoding, path.join resolves .. which allows traversal
        let targetPath = path.join(webRoot, requestPath);
        
        // Use realpathSync to resolve to actual filesystem path
        // This is similar to httpster's vulnerable usage
        try {
            targetPath = fs.realpathSync(targetPath);
        } catch (e) {
            // File doesn't exist, fall through to next handler
            return next();
        }
        
        // VULNERABLE: No validation that targetPath is still within webRoot
        // A secure implementation would check:
        // const resolvedWebRoot = fs.realpathSync(webRoot);
        // if (!targetPath.startsWith(resolvedWebRoot + path.sep) && targetPath !== resolvedWebRoot) {
        //     return res.status(403).send('Forbidden');
        // }
        
        // Check if it's a file and serve it
        const stats = fs.statSync(targetPath);
        if (stats.isFile()) {
            // Determine content type
            const ext = path.extname(targetPath).toLowerCase();
            const contentTypes = {
                '.html': 'text/html',
                '.css': 'text/css',
                '.js': 'application/javascript',
                '.json': 'application/json',
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.gif': 'image/gif',
                '.txt': 'text/plain',
            };
            const contentType = contentTypes[ext] || 'application/octet-stream';
            res.setHeader('Content-Type', contentType);
            return res.sendFile(targetPath);
        }
        
        // If it's a directory, fall through to serve-index
        next();
    } catch (e) {
        // On any error, fall through to static middleware
        next();
    }
});

// Serve static files from the web root
app.use(express.static(webRoot));

// Directory listing (like httpster's serveIndex)
app.use(serveIndex(webRoot, { icons: true }));

// 404 handler
app.use((req, res) => {
    res.status(404).send('Not Found');
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`File server running on port ${PORT}`);
    console.log(`Serving files from: ${webRoot}`);
});
