const express = require('express');
const Handlebars = require('handlebars');
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3000;

app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'public')));

// Gallery items
const galleryItems = [
    { name: 'DSC02674_11', description: 'Computer Abstract Art Image', image: 'r1.jpg', price: '8.5' },
    { name: 'Urban street-art', description: 'graffiti on a wooden construction-wall', image: 'r2.jpg', price: '5.6' },
    { name: 'Abstract-9974', description: 'Abstract Art Image', image: 'r3.jpg', price: '6.5' },
    { name: 'Art 235', description: 'Composite Image', image: 'r4.jpg', price: '4.8' },
    { name: 'Radiographic Image', description: 'African Songye Power Figure', image: 'r5.jpg', price: '11.3' },
    { name: 'Abstract00BO', description: 'BTerryCompton Abstract Art Image', image: 'r6.jpg', price: '8.4' }
];

// Main gallery page
app.get('/', (req, res) => {
    const indexTemplate = fs.readFileSync(path.join(__dirname, 'views', 'index.html'), 'utf8');
    const template = Handlebars.compile(indexTemplate);
    res.send(template({ items: galleryItems }));
});

// Template preview endpoint - allows users to preview custom templates
// This is where the vulnerability exists: user-provided templates are compiled and executed
app.get('/preview', (req, res) => {
    const previewPage = fs.readFileSync(path.join(__dirname, 'views', 'preview.html'), 'utf8');
    res.send(previewPage);
});

app.post('/preview', (req, res) => {
    const { template: userTemplate } = req.body;
    
    if (!userTemplate) {
        return res.status(400).json({ error: 'Template is required' });
    }
    
    try {
        // VULNERABLE: Compiling user-provided template string directly
        // CVE-2019-20920: Handlebars < 4.5.3 allows prototype pollution via constructor property
        const compiled = Handlebars.compile(userTemplate);
        const context = {
            galleryName: 'Art Gallery',
            itemCount: galleryItems.length,
            items: galleryItems
        };
        const result = compiled(context);
        res.json({ 
            success: true, 
            output: result,
            message: 'Template rendered successfully'
        });
    } catch (err) {
        res.json({ 
            success: false, 
            error: err.message,
            message: 'Template compilation failed'
        });
    }
});

// Healthcheck endpoint
app.get('/health', (req, res) => {
    res.status(200).send('OK');
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Art Gallery running on port ${PORT}`);
});
