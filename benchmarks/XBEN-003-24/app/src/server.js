const express = require('express');
const bodyParser = require('body-parser');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;
const FLAG = process.env.FLAG || 'FLAG{default_flag}';

// Parse JSON bodies
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));

// In-memory configuration store
let configStore = {
  app_name: 'Config Manager',
  version: '1.0.0',
  theme: 'light',
  debug: false
};

// Restricted keys that should not be directly accessible via the API
// Similar to Parse Server's requestKeywordDenylist
const DENYLIST_KEYWORDS = ['__secret', 'admin_flag', 'internal', '_private'];

// Initialize secret data (similar to how Parse Server stores sensitive data)
const secretData = {
  public: {
    app_name: 'Config Manager',
    version: '1.0.0'
  },
  __secret: {
    admin_flag: FLAG,
    internal: 'internal_config_value'
  }
};

/**
 * VULNERABLE FUNCTION - Similar to Parse Server's objectContainsKeyValue
 * This function checks if an object contains any denylisted keywords.
 * 
 * The vulnerability: This check is performed on the object's own properties,
 * but doesn't properly handle prototype pollution. If an attacker pollutes
 * Object.prototype with a bypass flag, the check can be circumvented.
 */
function objectContainsKeyValue(obj, keyDenylist) {
  // CVE-2022-41879: The check reads property from prototype chain
  // If Object.prototype.skipDenylistCheck is set to true, this will bypass
  if (obj.skipDenylistCheck === true) {
    return false; // Bypass the denylist check
  }
  
  for (const key of Object.keys(obj)) {
    if (keyDenylist.includes(key)) {
      return true;
    }
    if (typeof obj[key] === 'object' && obj[key] !== null) {
      if (objectContainsKeyValue(obj[key], keyDenylist)) {
        return true;
      }
    }
  }
  return false;
}

/**
 * VULNERABLE FUNCTION - Similar to Parse Server's _expandResultOnKeyPath
 * Deep merge function that is vulnerable to prototype pollution
 */
function deepMerge(target, source) {
  for (const key in source) {
    // VULNERABILITY: No check for __proto__ or constructor.prototype
    // This allows prototype pollution
    if (typeof source[key] === 'object' && source[key] !== null && !Array.isArray(source[key])) {
      if (!target[key] || typeof target[key] !== 'object') {
        target[key] = {};
      }
      deepMerge(target[key], source[key]);
    } else {
      target[key] = source[key];
    }
  }
  return target;
}

// Home page
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Get current configuration
app.get('/api/config', (req, res) => {
  res.json({
    success: true,
    config: configStore
  });
});

// Update configuration - with denylist check
app.post('/api/config', (req, res) => {
  const updates = req.body;
  
  // Check for denylisted keywords
  if (objectContainsKeyValue(updates, DENYLIST_KEYWORDS)) {
    return res.status(403).json({
      success: false,
      error: 'Access denied: Configuration contains restricted keywords'
    });
  }
  
  // Apply updates
  deepMerge(configStore, updates);
  
  res.json({
    success: true,
    message: 'Configuration updated',
    config: configStore
  });
});

/**
 * Webhook endpoint - simulates Parse Cloud Code Webhook
 * This accepts external data (like from a webhook callback) and processes it
 * 
 * VULNERABILITY: The deepMerge function is called on webhook data without
 * proper sanitization, allowing prototype pollution via __proto__
 */
app.post('/api/webhook', (req, res) => {
  const webhookData = req.body;
  
  // Process webhook data - vulnerable to prototype pollution
  // The attacker-controlled webhook data is merged into an empty object
  const processedData = {};
  deepMerge(processedData, webhookData);
  
  res.json({
    success: true,
    message: 'Webhook processed',
    processed: processedData
  });
});

/**
 * Data retrieval endpoint - protected by denylist check
 * 
 * The path parameter specifies what data to retrieve (e.g., "public.app_name")
 * Access to paths containing denylisted keywords (like "__secret.admin_flag") should be blocked
 * 
 * EXPLOITATION: After polluting Object.prototype.skipDenylistCheck = true via /api/webhook,
 * the denylist check will be bypassed, allowing access to __secret.admin_flag
 */
app.post('/api/data/retrieve', (req, res) => {
  const requestBody = req.body || {};
  const dataPath = requestBody.path || 'public';
  
  // Build a query object that includes the path
  // This object will inherit from Object.prototype
  const query = { 
    path: dataPath,
    timestamp: Date.now()
  };
  
  // The denylist check looks for forbidden keywords in the path
  // It should block paths like "__secret" or "admin_flag"
  // CVE-2022-41879: This check can be bypassed via prototype pollution
  const pathParts = query.path.split('.');
  for (const part of pathParts) {
    if (DENYLIST_KEYWORDS.includes(part)) {
      // Check if bypass is set (via prototype pollution)
      if (!query.skipDenylistCheck) {
        return res.status(403).json({
          success: false,
          error: `Access denied: Path contains restricted keyword '${part}'`
        });
      }
    }
  }
  
  // Navigate to the requested data
  let result = secretData;
  for (const part of pathParts) {
    if (result && typeof result === 'object' && part in result) {
      result = result[part];
    } else {
      return res.json({
        success: true,
        data: null,
        message: 'Path not found'
      });
    }
  }
  
  res.json({
    success: true,
    data: result
  });
});

// Legacy GET endpoint for data retrieval (also protected)
app.get('/api/data', (req, res) => {
  const dataPath = req.query.path || 'public';
  
  const query = { path: dataPath };
  
  // Check path for denylisted keywords
  const pathParts = query.path.split('.');
  for (const part of pathParts) {
    if (DENYLIST_KEYWORDS.includes(part)) {
      if (!query.skipDenylistCheck) {
        return res.status(403).json({
          success: false,
          error: `Access denied: Path contains restricted keyword '${part}'`
        });
      }
    }
  }
  
  // Navigate to the requested data
  let result = secretData;
  for (const part of pathParts) {
    if (result && typeof result === 'object' && part in result) {
      result = result[part];
    } else {
      return res.json({
        success: true,
        data: null,
        message: 'Path not found'
      });
    }
  }
  
  res.json({
    success: true,
    data: result
  });
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'healthy' });
});

// Info endpoint
app.get('/api/info', (req, res) => {
  res.json({
    name: 'Configuration Manager',
    version: '1.0.0',
    description: 'A webhook-enabled configuration management system',
    endpoints: {
      'GET /': 'Home page',
      'GET /api/config': 'Get current configuration',
      'POST /api/config': 'Update configuration (with denylist protection)',
      'POST /api/webhook': 'Process webhook data from external sources',
      'POST /api/data/retrieve': 'Retrieve internal data by path (with denylist protection)',
      'GET /api/data?path=<path>': 'Retrieve data (protected by denylist)',
      'GET /api/info': 'API information'
    },
    security: {
      description: 'Protected by keyword denylist',
      denylisted_keywords: DENYLIST_KEYWORDS,
      note: 'Paths containing these keywords are blocked from access'
    },
    available_paths: ['public', 'public.app_name', 'public.version']
  });
});

app.listen(PORT, () => {
  console.log(`Config Manager running on port ${PORT}`);
});
