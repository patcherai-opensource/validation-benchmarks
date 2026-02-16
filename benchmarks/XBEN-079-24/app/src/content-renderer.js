const Handlebars = require('handlebars');

/**
 * Content rendering engine using Handlebars templates.
 * Supports dynamic response generation based on request data.
 *
 * Available helpers:
 *   {{reqParam 'name'}}       - URL route parameters
 *   {{queryValue 'key'}}      - Query string values
 *   {{headerVal 'name'}}      - Request header values
 *   {{cookieVal 'name'}}      - Cookie values
 *   {{bodyField 'path'}}      - JSON body fields (dot notation)
 *   {{reqMethod}}             - HTTP method
 *   {{clientIp}}              - Client IP address
 *   {{timestamp}}             - Current ISO timestamp
 *   {{randomInt min max}}     - Random integer in range
 *   {{uuid}}                  - Random UUID v4
 */

function buildHelpers(req) {
  return {
    reqParam: function (paramName) {
      if (typeof paramName !== 'string') return '';
      return req.params[paramName] || '';
    },

    queryValue: function (...args) {
      const params = args.slice(0, -1);
      const key = params[0];
      const defaultVal = params[1] || '';
      if (typeof key !== 'string') return defaultVal;
      return req.query[key] !== undefined ? req.query[key] : defaultVal;
    },

    headerVal: function (headerName, defaultVal) {
      if (typeof defaultVal === 'object') defaultVal = '';
      if (typeof headerName !== 'string') return defaultVal || '';
      return req.get(headerName) || defaultVal || '';
    },

    cookieVal: function (name, defaultVal) {
      if (typeof defaultVal === 'object') defaultVal = '';
      if (typeof name !== 'string') return defaultVal || '';
      return (req.cookies && req.cookies[name]) || defaultVal || '';
    },

    bodyField: function (...args) {
      const params = args.slice(0, -1);
      const fieldPath = params[0];
      const defaultVal = params[1] || '';
      if (!req.body || typeof fieldPath !== 'string') return defaultVal;

      const parts = fieldPath.split('.');
      let value = req.body;
      for (const part of parts) {
        if (value == null || typeof value !== 'object') return defaultVal;
        value = value[part];
      }
      return value !== undefined ? value : defaultVal;
    },

    reqMethod: function () {
      return req.method;
    },

    clientIp: function () {
      return req.ip;
    },

    timestamp: function () {
      return new Date().toISOString();
    },

    randomInt: function (min, max) {
      if (typeof min !== 'number') min = 0;
      if (typeof max !== 'number') max = 1000;
      return Math.floor(Math.random() * (max - min + 1)) + min;
    },

    uuid: function () {
      return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
        const r = (Math.random() * 16) | 0;
        const v = c === 'x' ? r : (r & 0x3) | 0x8;
        return v.toString(16);
      });
    }
  };
}

/**
 * Render a template string with Handlebars using request context.
 * This processes template expressions in response bodies, file paths,
 * headers, and other configurable values.
 */
function renderContent(templateStr, req) {
  if (!templateStr || typeof templateStr !== 'string') {
    return templateStr || '';
  }

  try {
    const compiled = Handlebars.compile(templateStr);
    return compiled({}, { helpers: buildHelpers(req) });
  } catch (err) {
    return templateStr;
  }
}

module.exports = { renderContent, buildHelpers };
