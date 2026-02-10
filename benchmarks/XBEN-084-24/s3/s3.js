const http = require("http");
const fs = require("fs");
const path = require("path");

const PORT = 8333;
const STATIC_ROOT = path.join(__dirname, "public");

function decodeComponent(text) {
  try {
    const placeholder = '\0SLASH\0';
    const protected = text.replace(/%2[fF]/g, placeholder);
    const decoded = decodeURIComponent(protected);
    return decoded.replace(new RegExp(placeholder, 'g'), '%2F');
  } catch (e) {
    return text;
  }
}

function isHidden(decodedPath) {
  const segments = decodedPath.split('/').filter(s => s.length > 0);
  if (segments.length === 0) return false;
  return segments[0].startsWith('.');
}

// Get MIME type based on extension
function getMimeType(filePath) {
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
  return mimeTypes[ext] || 'application/octet-stream';
}

const server = http.createServer((req, res) => {
  // Only allow GET, HEAD, OPTIONS
  if (!['GET', 'HEAD', 'OPTIONS'].includes(req.method)) {
    res.writeHead(405, { 'Content-Type': 'text/plain' });
    res.end('Method Not Allowed');
    return;
  }

  if (req.method === 'OPTIONS') {
    res.writeHead(200, {
      'Allow': 'GET, HEAD, OPTIONS',
      'Content-Type': 'text/plain'
    });
    res.end();
    return;
  }

  let requestPath = req.url || '/';
  
  // Remove query string
  const queryIndex = requestPath.indexOf('?');
  if (queryIndex !== -1) {
    requestPath = requestPath.substring(0, queryIndex);
  }

  let decodedPath = decodeComponent(requestPath);
  
  if (decodedPath.startsWith('/')) {
    decodedPath = decodedPath.substring(1);
  }

  if (isHidden(decodedPath)) {
    res.writeHead(403, { 'Content-Type': 'text/plain' });
    res.end('Forbidden');
    return;
  }

  const fullyDecodedPath = decodedPath.replace(/%2[fF]/g, '/');
  const resolvedPath = path.normalize(fullyDecodedPath);
  
  // Construct final file path
  const filePath = path.join(STATIC_ROOT, resolvedPath);
  
  // Basic security: ensure we're still within STATIC_ROOT (prevent escaping)
  const normalizedRoot = path.normalize(STATIC_ROOT);
  const normalizedFile = path.normalize(filePath);
  
  if (!normalizedFile.startsWith(normalizedRoot)) {
    res.writeHead(403, { 'Content-Type': 'text/plain' });
    res.end('Forbidden');
    return;
  }

  // Check if file exists
  fs.stat(filePath, (err, stats) => {
    if (err) {
      if (err.code === 'ENOENT') {
        res.writeHead(404, { 'Content-Type': 'text/plain' });
        res.end('Not Found');
      } else {
        res.writeHead(500, { 'Content-Type': 'text/plain' });
        res.end('Internal Server Error');
      }
      return;
    }

    if (stats.isDirectory()) {
      // Try to serve index.html from directory
      const indexPath = path.join(filePath, 'index.html');
      fs.stat(indexPath, (indexErr, indexStats) => {
        if (indexErr || !indexStats.isFile()) {
          // List directory contents
          fs.readdir(filePath, (dirErr, files) => {
            if (dirErr) {
              res.writeHead(500, { 'Content-Type': 'text/plain' });
              res.end('Internal Server Error');
              return;
            }
            // Filter out hidden files from listing
            const visibleFiles = files.filter(f => !f.startsWith('.'));
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(visibleFiles));
          });
          return;
        }
        
        // Serve index.html
        serveFile(indexPath, res);
      });
      return;
    }

    serveFile(filePath, res);
  });
});

function serveFile(filePath, res) {
  const mimeType = getMimeType(filePath);
  
  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(500, { 'Content-Type': 'text/plain' });
      res.end('Internal Server Error');
      return;
    }
    
    res.writeHead(200, { 'Content-Type': mimeType });
    res.end(data);
  });
}

server.listen(PORT, '0.0.0.0', () => {
  console.log(`Static file server listening on port ${PORT}`);
});
