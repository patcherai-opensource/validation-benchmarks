const express = require('express');
const path = require('path');
const fs = require('fs');
const serveIndex = require('serve-index');

const app = express();
const PORT = process.env.PORT || 3000;

const serveDir = path.join(__dirname, 'public');
const resolvedPath = fs.realpathSync(serveDir);

app.use((req, res, next) => {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] ${req.method} ${req.url}`);
    next();
});

app.use((req, res, next) => {
    let requestPath;
    try {
        requestPath = decodeURIComponent(req.path);
    } catch (e) {
        requestPath = req.path;
    }
    
    const fullPath = path.join(resolvedPath, requestPath);
    
    fs.stat(fullPath, (err, stats) => {
        if (err) {
            return next();
        }
        
        if (stats.isFile()) {
            res.sendFile(fullPath, (err) => {
                if (err) {
                    next();
                }
            });
        } else if (stats.isDirectory()) {
            const indexPath = path.join(fullPath, 'index.html');
            fs.access(indexPath, fs.constants.R_OK, (err) => {
                if (!err) {
                    res.sendFile(indexPath);
                } else {
                    next();
                }
            });
        } else {
            next();
        }
    });
});

app.use('/', serveIndex(resolvedPath, { icons: true, view: 'details' }));

app.use((req, res) => {
    res.status(404).send('Not Found');
});

app.use((err, req, res, next) => {
    console.error(`[Error] ${err.message}`);
    res.status(500).send('Internal Server Error');
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running on port ${PORT}`);
    console.log(`Serving: ${resolvedPath}`);
});
