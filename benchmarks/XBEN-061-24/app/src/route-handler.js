const fs = require('fs');
const path = require('path');
const mime = require('mime-types');
const { parseTemplate } = require('./template-engine');

/**
 * Resolve a file path relative to the environment base directory.
 * If the path is already absolute, use it as-is.
 */
function resolveResponsePath(filePath, baseDirectory) {
  if (path.isAbsolute(filePath)) {
    return filePath;
  }
  return path.resolve(baseDirectory, filePath);
}

/**
 * Serve a response from a file whose path may contain template expressions.
 * The filePath is first processed through the template engine, which can
 * substitute request data (query params, url params, headers, etc.).
 */
function serveFileResponse(routeConfig, req, res, baseDirectory) {
  try {
    // Process the file path template with request context
    let filePath = parseTemplate(
      routeConfig.filePath.replace(/\\(?!\.)/g, '/'),
      req
    );

    filePath = resolveResponsePath(filePath, baseDirectory);

    const fileMimeType = mime.lookup(filePath) || 'application/octet-stream';

    // Set appropriate content type
    if (routeConfig.contentType) {
      res.set('Content-Type', routeConfig.contentType);
    } else if (fileMimeType) {
      res.set('Content-Type', fileMimeType);
    }

    // Check if file exists and is not a directory
    if (!fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
      if (routeConfig.fallbackTo404) {
        res.status(404).json({ error: 'Resource not found' });
      } else {
        res.status(500).json({
          error: 'The requested file could not be served',
          statusCode: 500
        });
      }
      return;
    }

    const data = fs.readFileSync(filePath);

    // For text-based content types, also parse templates within the file content
    if (isTemplateCompatible(fileMimeType)) {
      const content = parseTemplate(data.toString(), req);
      res.send(content);
    } else {
      res.set('Content-Length', data.length.toString());
      res.send(data);
    }

  } catch (err) {
    res.status(500).json({ error: 'Internal server error processing response' });
  }
}

/**
 * Serve an inline body response, optionally processing templates.
 */
function serveBodyResponse(routeConfig, req, res) {
  try {
    if (routeConfig.contentType) {
      res.set('Content-Type', routeConfig.contentType);
    } else {
      res.set('Content-Type', 'application/json');
    }

    let content = routeConfig.body || '';

    if (!routeConfig.disableTemplating) {
      content = parseTemplate(content, req);
    }

    res.status(routeConfig.statusCode || 200).send(content);
  } catch (err) {
    res.status(500).json({ error: 'Internal server error processing response' });
  }
}

function isTemplateCompatible(mimeType) {
  const templateTypes = [
    'application/json',
    'text/html',
    'text/plain',
    'text/xml',
    'application/xml',
    'text/css',
    'application/javascript',
    'text/csv'
  ];
  return templateTypes.some(t => mimeType.includes(t));
}

module.exports = { serveFileResponse, serveBodyResponse, resolveResponsePath };
