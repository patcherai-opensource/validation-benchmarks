/**
 * Response rules interpreter.
 * Evaluates conditions to determine which response variant to serve
 * for a given route. Supports matching on query params, headers,
 * body fields, URL params, and cookies.
 */

function matchRule(rule, req) {
  let actual = '';

  switch (rule.target) {
    case 'query':
      actual = req.query[rule.modifier] || '';
      break;
    case 'header':
      actual = req.get(rule.modifier) || '';
      break;
    case 'body':
      if (req.body && rule.modifier) {
        const parts = rule.modifier.split('.');
        let val = req.body;
        for (const p of parts) {
          if (val == null) break;
          val = val[p];
        }
        actual = val != null ? String(val) : '';
      }
      break;
    case 'params':
      actual = req.params[rule.modifier] || '';
      break;
    case 'cookie':
      actual = (req.cookies && req.cookies[rule.modifier]) || '';
      break;
    default:
      return false;
  }

  const expected = rule.value || '';

  switch (rule.operator) {
    case 'equals':
      return actual === expected;
    case 'contains':
      return actual.includes(expected);
    case 'regex':
      try {
        return new RegExp(expected).test(actual);
      } catch {
        return false;
      }
    case 'exists':
      return actual !== '';
    default:
      return actual === expected;
  }
}

/**
 * Evaluate response rules for a route and return the matching
 * response variant. Falls back to the first response if no
 * rules match.
 */
function evaluateResponseRules(route, req) {
  if (!route.responses || route.responses.length === 0) {
    return {
      statusCode: 200,
      body: '',
      bodyType: 'inline',
      headers: []
    };
  }

  // Default response is the first one
  const defaultResponse = route.responses[0];

  // Check subsequent responses for matching rules
  for (let i = 1; i < route.responses.length; i++) {
    const resp = route.responses[i];
    if (resp.rules && resp.rules.length > 0) {
      const allMatch = resp.rulesOperator === 'OR'
        ? resp.rules.some((r) => matchRule(r, req))
        : resp.rules.every((r) => matchRule(r, req));

      if (allMatch) {
        return resp;
      }
    }
  }

  return defaultResponse;
}

module.exports = { evaluateResponseRules };
