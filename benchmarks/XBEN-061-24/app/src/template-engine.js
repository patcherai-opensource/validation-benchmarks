const Handlebars = require('handlebars');

/**
 * Build template helpers that have access to the incoming request context.
 * Mirrors the Handlebars helper pattern used by our response rendering engine.
 */
function buildRequestHelpers(req) {
  return {
    queryParam: function (...args) {
      const params = args.slice(0, -1);
      const paramName = params[0] || '';
      const defaultValue = params[1] || '';

      if (!paramName || !req.query) {
        return defaultValue;
      }

      const value = req.query[paramName];
      if (value === undefined || value === null) {
        return defaultValue;
      }

      if (typeof value === 'object') {
        return new Handlebars.SafeString(JSON.stringify(value));
      }
      return new Handlebars.SafeString(value);
    },

    urlParam: function (...args) {
      const params = args.slice(0, -1);
      const paramName = params[0] || '';
      const defaultValue = params[1] || '';

      if (!paramName || !req.params) {
        return defaultValue;
      }

      return req.params[paramName] || defaultValue;
    },

    header: function (...args) {
      const params = args.slice(0, -1);
      const headerName = params[0] || '';
      const defaultValue = params[1] || '';

      if (!headerName) {
        return defaultValue;
      }

      return req.get(headerName) || defaultValue;
    },

    cookie: function (...args) {
      const params = args.slice(0, -1);
      const cookieName = params[0] || '';
      const defaultValue = params[1] || '';

      if (!cookieName || !req.cookies) {
        return defaultValue;
      }

      return req.cookies[cookieName] || defaultValue;
    },

    body: function (...args) {
      const params = args.slice(0, -1);
      const path = params[0] || '';
      const defaultValue = params[1] || '';

      if (!path || !req.body) {
        return req.body ? JSON.stringify(req.body) : defaultValue;
      }

      const parts = path.split('.');
      let value = req.body;
      for (const part of parts) {
        if (value && typeof value === 'object' && part in value) {
          value = value[part];
        } else {
          return defaultValue;
        }
      }

      if (typeof value === 'object') {
        return new Handlebars.SafeString(JSON.stringify(value));
      }
      return new Handlebars.SafeString(String(value));
    },

    now: function () {
      return new Date().toISOString();
    },

    hostname: function () {
      return req.hostname || 'localhost';
    },

    ip: function () {
      return req.ip || '127.0.0.1';
    },

    method: function () {
      return req.method;
    }
  };
}

/**
 * Parse template content using Handlebars with request-aware helpers.
 * This is the core templating function used to process response bodies
 * and file paths before serving.
 */
function parseTemplate(content, req) {
  if (!content || typeof content !== 'string') {
    return content || '';
  }

  const helpers = buildRequestHelpers(req);
  const compiled = Handlebars.compile(content, { noEscape: true });
  return compiled({}, { helpers });
}

module.exports = { parseTemplate, buildRequestHelpers };
