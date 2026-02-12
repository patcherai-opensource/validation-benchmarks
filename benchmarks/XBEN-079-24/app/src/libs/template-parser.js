'use strict';

const Handlebars = require('handlebars');

/**
 * TemplateParser - processes Handlebars templates with request context.
 * Used for dynamic route responses, file paths, headers, etc.
 */
class TemplateParser {
  constructor() {
    this.handlebars = Handlebars.create();
    this._registerHelpers();
  }

  _registerHelpers() {
    // Helper to access query parameters
    this.handlebars.registerHelper('queryParam', function (paramName, options) {
      const request = options.data.root.request;
      if (request && request.query && request.query[paramName] !== undefined) {
        return new Handlebars.SafeString(request.query[paramName]);
      }
      return '';
    });

    // Helper to access URL parameters
    this.handlebars.registerHelper('urlParam', function (paramName, options) {
      const request = options.data.root.request;
      if (request && request.params && request.params[paramName] !== undefined) {
        return new Handlebars.SafeString(request.params[paramName]);
      }
      return '';
    });

    // Helper to access request body fields
    this.handlebars.registerHelper('body', function (path, options) {
      const request = options.data.root.request;
      if (request && request.body) {
        const parts = path.split('.');
        let val = request.body;
        for (const part of parts) {
          if (val && typeof val === 'object' && part in val) {
            val = val[part];
          } else {
            return '';
          }
        }
        return new Handlebars.SafeString(String(val));
      }
      return '';
    });

    // Helper to access request headers
    this.handlebars.registerHelper('header', function (headerName, options) {
      const request = options.data.root.request;
      if (request && request.headers && request.headers[headerName.toLowerCase()] !== undefined) {
        return new Handlebars.SafeString(request.headers[headerName.toLowerCase()]);
      }
      return '';
    });

    // Helper for current timestamp
    this.handlebars.registerHelper('now', function () {
      return new Handlebars.SafeString(new Date().toISOString());
    });

    // Helper for generating random integer
    this.handlebars.registerHelper('int', function (min, max) {
      return Math.floor(Math.random() * (max - min + 1)) + min;
    });
  }

  /**
   * Parse a template string with request context data
   * @param {string} templateStr - Handlebars template string
   * @param {object} request - Express request object
   * @returns {string} - Resolved template string
   */
  parse(templateStr, request) {
    try {
      const template = this.handlebars.compile(templateStr, { noEscape: true });
      return template({ request });
    } catch (err) {
      return templateStr;
    }
  }
}

module.exports = { TemplateParser };
