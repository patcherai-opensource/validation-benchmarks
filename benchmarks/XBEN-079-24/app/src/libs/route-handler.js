'use strict';

const fs = require('fs');
const path = require('path');
const mime = require('mime-types');
const { TemplateParser } = require('./template-parser');

const templateParser = new TemplateParser();

/**
 * Send a file response using the configured filePath template.
 * The filePath is processed through TemplateParser to resolve
 * dynamic segments from the request context.
 */
function sendFile(res, filePath, request, baseDir) {
  // Process the filePath template with request data
  const resolvedPath = templateParser.parse(filePath, request);

  // Construct the full path relative to the data directory
  const fullPath = path.join(baseDir, resolvedPath);

  // Attempt to read and return the file
  fs.readFile(fullPath, (err, data) => {
    if (err) {
      if (err.code === 'ENOENT') {
        res.status(404).json({
          error: 'File not found',
          status: 404
        });
      } else {
        res.status(500).json({
          error: 'Internal server error',
          status: 500
        });
      }
      return;
    }

    const contentType = mime.lookup(fullPath) || 'application/octet-stream';
    res.set('Content-Type', contentType);
    res.status(200).send(data);
  });
}

/**
 * Send a file with a callback for completion tracking.
 * Used by routes that need post-send processing.
 */
function sendFileWithCallback(res, filePath, request, baseDir, callback) {
  const resolvedPath = templateParser.parse(filePath, request);
  const fullPath = path.join(baseDir, resolvedPath);

  fs.readFile(fullPath, (err, data) => {
    if (err) {
      if (err.code === 'ENOENT') {
        res.status(404).json({ error: 'File not found', status: 404 });
      } else {
        res.status(500).json({ error: 'Internal server error', status: 500 });
      }
      if (callback) callback(err);
      return;
    }

    const contentType = mime.lookup(fullPath) || 'application/octet-stream';
    res.set('Content-Type', contentType);
    res.status(200).send(data);
    if (callback) callback(null);
  });
}

/**
 * Send a JSON body response, also processed through TemplateParser.
 */
function sendJsonBody(res, bodyTemplate, request, statusCode) {
  const resolvedBody = templateParser.parse(bodyTemplate, request);
  try {
    const parsed = JSON.parse(resolvedBody);
    res.status(statusCode || 200).json(parsed);
  } catch (e) {
    res.status(statusCode || 200).set('Content-Type', 'application/json').send(resolvedBody);
  }
}

module.exports = { sendFile, sendFileWithCallback, sendJsonBody, templateParser };
