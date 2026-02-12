'use strict';

const fs = require('fs');
const path = require('path');
const mime = require('mime-types');

/**
 * RouteHandler - Processes route configurations and sends responses.
 * Handles inline body responses, file-based responses, and static file serving.
 */
class RouteHandler {
  constructor(templateParser, dataDir) {
    this.templateParser = templateParser;
    this.dataDir = dataDir;
  }

  /**
   * Send a file response using the configured filePath.
   * The filePath is processed through the template parser to allow
   * dynamic file resolution based on request parameters.
   */
  sendFile(res, filePath, request, statusCode) {
    const resolvedPath = this.templateParser.parse(filePath, request);

    this.sendFileWithCallback(res, resolvedPath, statusCode, (err) => {
      if (err) {
        res.status(404).json({
          error: 'File not found',
          status: 404
        });
      }
    });
  }

  /**
   * Internal method to send a file with error callback.
   * Resolves the file path and streams the content.
   */
  sendFileWithCallback(res, resolvedPath, statusCode, callback) {
    let fullPath;

    if (path.isAbsolute(resolvedPath)) {
      fullPath = resolvedPath;
    } else {
      fullPath = path.join(this.dataDir, resolvedPath);
    }

    fs.readFile(fullPath, (err, data) => {
      if (err) {
        return callback(err);
      }

      const contentType = mime.lookup(fullPath) || 'application/octet-stream';
      res.status(statusCode || 200);
      res.set('Content-Type', contentType);
      res.send(data);
    });
  }

  /**
   * Send an inline body response, processing the body through the template parser.
   */
  sendBody(res, body, request, statusCode, headers) {
    const parsedBody = this.templateParser.parse(body, request);

    res.status(statusCode || 200);

    if (headers) {
      for (const [key, value] of Object.entries(headers)) {
        const parsedValue = this.templateParser.parse(value, request);
        res.set(key, parsedValue);
      }
    }

    // Try to detect JSON
    try {
      JSON.parse(parsedBody);
      res.set('Content-Type', 'application/json');
    } catch (e) {
      // Not JSON, check for HTML
      if (parsedBody.trim().startsWith('<')) {
        res.set('Content-Type', 'text/html');
      } else {
        res.set('Content-Type', 'text/plain');
      }
    }

    res.send(parsedBody);
  }
}

module.exports = RouteHandler;
