const fs = require('fs');
const path = require('path');
const mimeTypes = require('mime-types');
const { renderContent } = require('./content-renderer');
const { evaluateResponseRules } = require('./rules-engine');

// Mime types that support templating in file content
const TEMPLATABLE_TYPES = [
  'text/html',
  'text/plain',
  'text/css',
  'application/json',
  'application/xml',
  'text/xml',
  'text/csv',
  'application/javascript'
];

const TEMPLATABLE_EXTENSIONS = [
  '.html', '.htm', '.json', '.xml', '.csv', '.txt', '.css', '.js'
];

/**
 * Resolve a file path. If the path is not absolute, resolve it
 * relative to the environment data directory.
 */
function resolveResponsePath(filePath, dataDir) {
  if (path.isAbsolute(filePath)) {
    return filePath;
  }
  return path.resolve(dataDir, filePath);
}

/**
 * Serve a file response for a route. The filePath from the route
 * response config is processed through the template engine to allow
 * dynamic file selection based on request parameters.
 */
function serveFileResponse(routeResponse, route, envConfig, req, res) {
  try {
    // Process the filePath template with request context
    let filePath = renderContent(
      routeResponse.filePath.replace(/\\(?!\.)/g, '/'),
      req
    );

    // Resolve relative paths against the data directory
    filePath = resolveResponsePath(filePath, envConfig.dataDir);

    const fileMime = mimeTypes.lookup(filePath) || '';

    if (fileMime && !res.getHeader('Content-Type')) {
      res.set('Content-Type', fileMime);
    }

    // Check if file should be sent as download attachment
    if (!routeResponse.sendAsBody) {
      res.set('Content-Disposition',
        `attachment; filename="${path.basename(filePath)}"`
      );
    }

    // For templatable file types, process the file content through
    // the template engine as well
    if (
      (TEMPLATABLE_TYPES.includes(fileMime) ||
        TEMPLATABLE_EXTENSIONS.includes(path.extname(filePath))) &&
      !routeResponse.disableTemplating
    ) {
      fs.readFile(filePath, (err, data) => {
        if (err) {
          if (routeResponse.fallbackTo404) {
            res.status(404);
            serveBodyResponse(routeResponse, route, envConfig, req, res);
          } else {
            res.status(500).json({ error: 'File serving error' });
          }
          return;
        }

        try {
          const rendered = renderContent(data.toString(), req);
          res.send(rendered);
        } catch (renderErr) {
          res.status(500).json({ error: 'File serving error' });
        }
      });
    } else {
      // For binary/non-templatable types, stream the file directly
      if (!fs.existsSync(filePath)) {
        if (routeResponse.fallbackTo404) {
          res.status(404);
          serveBodyResponse(routeResponse, route, envConfig, req, res);
        } else {
          res.status(500).json({ error: 'File serving error' });
        }
        return;
      }

      const stat = fs.statSync(filePath);
      res.set('Content-Length', stat.size.toString());
      const stream = fs.createReadStream(filePath);
      stream.pipe(res);
    }
  } catch (err) {
    res.status(500).json({ error: 'File serving error' });
  }
}

/**
 * Serve an inline body response. The body content is processed
 * through the template engine.
 */
function serveBodyResponse(routeResponse, route, envConfig, req, res) {
  try {
    const body = routeResponse.body || '';
    if (!routeResponse.disableTemplating) {
      const rendered = renderContent(body, req);
      res.send(rendered);
    } else {
      res.send(body);
    }
  } catch (err) {
    res.status(500).json({ error: 'Response generation error' });
  }
}

/**
 * Handle an incoming request matched to a route definition.
 * Selects the appropriate response based on rules, applies
 * latency, headers, and serves the response.
 */
function handleRouteRequest(route, envConfig, req, res) {
  // Select the active response (evaluate rules if multiple responses)
  const activeResponse = evaluateResponseRules(route, req);

  // Apply configured status code
  res.status(activeResponse.statusCode || 200);

  // Apply response headers
  if (activeResponse.headers && Array.isArray(activeResponse.headers)) {
    activeResponse.headers.forEach((h) => {
      try {
        const val = renderContent(h.value, req);
        res.set(h.key, val);
      } catch (e) {
        // skip invalid headers
      }
    });
  }

  // Apply environment-level headers
  if (envConfig.headers && Array.isArray(envConfig.headers)) {
    envConfig.headers.forEach((h) => {
      if (!res.getHeader(h.key)) {
        try {
          res.set(h.key, renderContent(h.value, req));
        } catch (e) {
          // skip
        }
      }
    });
  }

  // Apply latency if configured
  const latency = activeResponse.latency || 0;

  const sendResponse = () => {
    if (activeResponse.bodyType === 'file' && activeResponse.filePath) {
      serveFileResponse(activeResponse, route, envConfig, req, res);
    } else {
      serveBodyResponse(activeResponse, route, envConfig, req, res);
    }
  };

  if (latency > 0) {
    setTimeout(sendResponse, latency);
  } else {
    sendResponse();
  }
}

/**
 * Register all routes from the environment configuration onto
 * the Express application.
 */
function createMockRoutes(app, envConfig) {
  const prefix = envConfig.endpointPrefix ? `/${envConfig.endpointPrefix}` : '';

  envConfig.routes.forEach((route) => {
    const fullPath = `${prefix}${route.endpoint}`;
    const method = (route.method || 'get').toLowerCase();

    if (typeof app[method] === 'function') {
      app[method](fullPath, (req, res) => {
        handleRouteRequest(route, envConfig, req, res);
      });
    }
  });

  // Catch-all for undefined routes within the API prefix
  if (prefix) {
    app.all(`${prefix}/*`, (req, res) => {
      res.status(404).json({
        error: 'Route not found',
        path: req.path
      });
    });
  }
}

module.exports = { createMockRoutes };
