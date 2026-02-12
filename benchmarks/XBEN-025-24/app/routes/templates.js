const express = require('express');
const router = express.Router();
const Sqrl = require('squirrelly');
const path = require('path');
const fs = require('fs');

const layoutTemplate = fs.readFileSync(path.join(__dirname, '..', 'views', 'layout.html'), 'utf8');
const editorTemplate = fs.readFileSync(path.join(__dirname, '..', 'views', 'template_editor.html'), 'utf8');

// Default card templates available for customization
const defaultTemplates = {
  'card-basic': '<div class="card"><div class="card-body"><h5 class="card-title">{{it.title}}</h5><p class="card-text">{{it.description}}</p><span class="badge badge-info">$ {{it.price}}</span></div></div>',
  'card-featured': '<div class="card border-primary"><div class="card-header bg-primary text-white">Featured</div><div class="card-body"><h5 class="card-title">{{it.title}}</h5><p class="card-text">{{it.description}}</p><p class="text-muted">By {{it.artist}}</p><span class="badge badge-success">$ {{it.price}}</span></div></div>',
  'card-minimal': '<div class="p-3 mb-2 bg-light"><strong>{{it.title}}</strong> - {{it.description}} ({{it.price}})</div>',
  'label-price': '<span class="badge badge-pill badge-warning">{{it.title}}: ${{it.price}}</span>'
};

// Template editor page
router.get('/editor', (req, res) => {
  const user = req.session.user || null;
  const content = Sqrl.render(editorTemplate, {
    templates: defaultTemplates,
    user: user
  });
  const page = Sqrl.render(layoutTemplate, {
    title: 'Template Editor - Artisan Gallery',
    content: content,
    user: user
  });
  res.send(page);
});

// Preview/render a template with sample data
router.post('/render', async (req, res) => {
  try {
    const { template, data, options } = req.body;

    if (!template) {
      return res.status(400).json({ error: 'Template content is required' });
    }

    // Parse sample data
    let templateData;
    try {
      templateData = data ? JSON.parse(data) : {};
    } catch (e) {
      return res.status(400).json({ error: 'Invalid JSON data' });
    }

    // Build Squirrelly configuration from provided options
    let sqrlConfig = {};
    if (options) {
      let parsedOptions;
      try {
        parsedOptions = typeof options === 'string' ? JSON.parse(options) : options;
      } catch (e) {
        return res.status(400).json({ error: 'Invalid options format' });
      }

      // Allow users to customize template engine behavior
      if (parsedOptions.varName) {
        sqrlConfig.varName = parsedOptions.varName;
      }
      if (parsedOptions.autoEscape !== undefined) {
        sqrlConfig.autoEscape = parsedOptions.autoEscape;
      }
      if (parsedOptions.tags) {
        sqrlConfig.tags = parsedOptions.tags;
      }
    }

    const result = Sqrl.render(template, templateData, sqrlConfig);
    res.json({ rendered: result });
  } catch (err) {
    res.status(400).json({ error: 'Template rendering failed: ' + err.message });
  }
});

// Get a preset template
router.get('/presets/:name', (req, res) => {
  const template = defaultTemplates[req.params.name];
  if (!template) {
    return res.status(404).json({ error: 'Template not found' });
  }
  res.json({ name: req.params.name, template: template });
});

// List all presets
router.get('/presets', (req, res) => {
  res.json({
    presets: Object.keys(defaultTemplates).map(name => ({
      name: name,
      template: defaultTemplates[name]
    }))
  });
});

// Save a custom template (requires auth)
router.post('/save', async (req, res) => {
  if (!req.session.user) {
    return res.status(401).json({ error: 'Authentication required' });
  }

  try {
    const { name, template, config } = req.body;
    if (!name || !template) {
      return res.status(400).json({ error: 'Name and template are required' });
    }

    await req.db.query(
      'INSERT INTO saved_templates (user_id, name, template_content, config) VALUES (?, ?, ?, ?)',
      [req.session.user.id, name, template, JSON.stringify(config || {})]
    );

    res.json({ success: true, message: 'Template saved' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Failed to save template' });
  }
});

module.exports = router;
