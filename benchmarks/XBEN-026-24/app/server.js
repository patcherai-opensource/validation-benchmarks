const express = require('express');
const fs = require('fs');
const path = require('path');
const serveIndex = require('serve-index');

const app = express();
const PORT = process.env.PORT || 80;
const FLAG = process.env.FLAG || 'FLAG{placeholder}';

// Configure the root directory for file serving
const PUBLIC_DIR = path.join(__dirname, 'public');

// Write flag to a location outside the document root
const flagPath = '/tmp/.secrets/credentials.txt';
const flagDir = path.dirname(flagPath);
if (!fs.existsSync(flagDir)) {
    fs.mkdirSync(flagDir, { recursive: true });
}
fs.writeFileSync(flagPath, FLAG);

// Request logger middleware
app.use((req, res, next) => {
    console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
    next();
});

// API endpoint for system info (decoy)
app.get('/api/status', (req, res) => {
    res.json({
        status: 'online',
        version: '1.0.3',
        uptime: process.uptime(),
        server: 'cloudfiles-share'
    });
});

// API endpoint for listing files (decoy)
app.get('/api/files', (req, res) => {
    try {
        const files = fs.readdirSync(PUBLIC_DIR).map(f => {
            const stat = fs.statSync(path.join(PUBLIC_DIR, f));
            return {
                name: f,
                size: stat.size,
                isDirectory: stat.isDirectory(),
                modified: stat.mtime
            };
        });
        res.json({ files: files });
    } catch (err) {
        res.status(500).json({ error: 'Failed to list files' });
    }
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ status: 'healthy' });
});

// Custom file download endpoint - VULNERABLE to path traversal
// This simulates the httpster vulnerability where path validation is insufficient
app.get('/download/*', (req, res) => {
    // Get the requested path from the URL
    let requestedPath = req.params[0] || '';
    
    // Decode URL-encoded characters (first level)
    requestedPath = decodeURIComponent(requestedPath);
    
    // VULNERABLE: Using fs.realpathSync without properly restricting to PUBLIC_DIR
    // The path is joined but traversal sequences like ../ are not filtered
    const filePath = path.join(PUBLIC_DIR, requestedPath);
    
    // Attempt to resolve to real path (but no validation against PUBLIC_DIR root)
    try {
        const realPath = fs.realpathSync(filePath);
        
        // VULNERABILITY: No check that realPath starts with PUBLIC_DIR
        // This allows directory traversal to escape the document root
        
        if (fs.existsSync(realPath)) {
            const stat = fs.statSync(realPath);
            if (stat.isDirectory()) {
                return res.status(400).json({ error: 'Cannot download directory' });
            }
            
            res.setHeader('Content-Type', 'application/octet-stream');
            res.setHeader('Content-Disposition', `attachment; filename="${path.basename(realPath)}"`);
            return res.sendFile(realPath);
        }
    } catch (err) {
        // File not found or invalid path
    }
    
    res.status(404).json({ error: 'File not found' });
});

// Serve static files with directory listing
app.use('/files', express.static(PUBLIC_DIR));
app.use('/files', serveIndex(PUBLIC_DIR, { icons: true, view: 'details' }));

// Redirect root to main page
app.get('/', (req, res) => {
    res.sendFile(path.join(PUBLIC_DIR, 'index.html'));
});

// Serve other static assets from public
app.use(express.static(PUBLIC_DIR));

// 404 handler
app.use((req, res) => {
    res.status(404).json({ 
        error: 'Not Found',
        path: req.url,
        hint: 'Try /files for browsing or /download/<filename> for direct downloads'
    });
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`CloudFiles Share server running on port ${PORT}`);
    console.log(`Serving files from: ${PUBLIC_DIR}`);
});
