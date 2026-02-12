'use strict';

const Handlebars = require('handlebars');

/**
 * TemplateParser - Processes Handlebars-style templates with request context.
 * Supports helpers: queryParam, header, body, urlParam, hostname, ip, method
 */
class TemplateParser {
  constructor() {
    this._registerHelpers();
  }

  _registerHelpers() {
    Handlebars.registerHelper('queryParam', function () {
      const args = Array.prototype.slice.call(arguments);
      const options = args[args.length - 1];
      const paramName = args[0];
      const defaultValue = args.length > 2 ? args[1] : '';

      if (options.data && options.data.request) {
        const val = options.data.request.query[paramName];
        return val !== undefined ? val : defaultValue;
      }
      return defaultValue;
    });

    Handlebars.registerHelper('urlParam', function () {
      const args = Array.prototype.slice.call(arguments);
      const options = args[args.length - 1];
      const paramName = args[0];

      if (options.data && options.data.request) {
        const val = options.data.request.params[paramName];
        return val !== undefined ? val : '';
      }
      return '';
    });

    Handlebars.registerHelper('header', function () {
      const args = Array.prototype.slice.call(arguments);
      const options = args[args.length - 1];
      const headerName = args[0];

      if (options.data && options.data.request) {
        const val = options.data.request.headers[headerName.toLowerCase()];
        return val !== undefined ? val : '';
      }
      return '';
    });

    Handlebars.registerHelper('body', function () {
      const args = Array.prototype.slice.call(arguments);
      const options = args[args.length - 1];
      const path = args[0];

      if (options.data && options.data.request && options.data.request.body) {
        const parts = path ? path.split('.') : [];
        let current = options.data.request.body;
        for (const part of parts) {
          if (current && typeof current === 'object') {
            current = current[part];
          } else {
            return '';
          }
        }
        return current !== undefined ? current : '';
      }
      return '';
    });

    Handlebars.registerHelper('hostname', function (options) {
      if (options.data && options.data.request) {
        return options.data.request.hostname || '';
      }
      return '';
    });

    Handlebars.registerHelper('ip', function (options) {
      if (options.data && options.data.request) {
        return options.data.request.ip || '';
      }
      return '';
    });

    Handlebars.registerHelper('method', function (options) {
      if (options.data && options.data.request) {
        return options.data.request.method || '';
      }
      return '';
    });

    Handlebars.registerHelper('now', function (format) {
      return new Date().toISOString();
    });

    Handlebars.registerHelper('oneOf', function () {
      const args = Array.prototype.slice.call(arguments);
      args.pop(); // remove options
      const idx = Math.floor(Math.random() * args.length);
      return args[idx];
    });
  }

  /**
   * Parse a template string with request context data.
   * Used for response bodies, file paths, and headers.
   */
  parse(templateStr, request) {
    if (!templateStr || typeof templateStr !== 'string') {
      return templateStr || '';
    }

    try {
      const compiled = Handlebars.compile(templateStr, { noEscape: true });
      return compiled({}, {
        data: { request: request }
      });
    } catch (err) {
      return templateStr;
    }
  }
}

module.exports = TemplateParser;
