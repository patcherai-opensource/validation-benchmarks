const express = require('express');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 5003;
const FLAG = process.env.FLAG || 'flag{test_flag}';

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'static')));

// Database connection
const MONGO_URI = process.env.MONGO_URI || 'mongodb://localhost:27017/dataprocessor';

mongoose.connect(MONGO_URI)
    .then(() => {
        console.log('Connected to MongoDB');
        initializeData();
    })
    .catch(err => console.error('MongoDB connection error:', err));

// Schema definitions
const DataRecordSchema = new mongoose.Schema({
    name: String,
    type: String,
    content: mongoose.Schema.Types.Mixed,
    restricted: { type: Boolean, default: false },
    createdAt: { type: Date, default: Date.now }
});

const DataRecord = mongoose.model('DataRecord', DataRecordSchema);

// Configuration object for security settings
const config = {
    requestKeywordDenylist: ['admin', 'secret', 'flag', 'restricted', 'internal'],
    maxResults: 100,
    allowedTypes: ['public', 'user']
};

// Initialize sample data
async function initializeData() {
    await DataRecord.deleteMany({});
    
    // Public records
    await DataRecord.create([
        { name: 'Welcome Message', type: 'public', content: { message: 'Welcome to the Data Processing Service' }, restricted: false },
        { name: 'User Guide', type: 'public', content: { guide: 'Use POST /api/process to query data' }, restricted: false },
        { name: 'Sample Record 1', type: 'user', content: { data: 'Sample user data 1' }, restricted: false },
        { name: 'Sample Record 2', type: 'user', content: { data: 'Sample user data 2' }, restricted: false },
        { name: 'Configuration', type: 'public', content: { version: '1.0.0' }, restricted: false }
    ]);
    
    // Internal records
    await DataRecord.create([
        { name: 'Admin Settings', type: 'internal', content: { setting: 'admin configuration' }, restricted: true },
        { name: 'Secret Key', type: 'internal', content: { key: FLAG }, restricted: true }
    ]);
    
    console.log('Data initialized');
}

// Deep merge utility for combining configuration objects
function deepMerge(target, source) {
    for (const key in source) {
        if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
            if (!target[key]) {
                target[key] = {};
            }
            deepMerge(target[key], source[key]);
        } else {
            target[key] = source[key];
        }
    }
    return target;
}

// Check if object contains any denylisted keywords
function objectContainsKeyValue(obj, denylist) {
    if (!obj || typeof obj !== 'object') return false;
    
    for (const key in obj) {
        if (denylist.includes(key.toLowerCase())) {
            return true;
        }
        if (denylist.some(keyword => String(obj[key]).toLowerCase().includes(keyword))) {
            return true;
        }
        if (typeof obj[key] === 'object' && obj[key] !== null) {
            if (objectContainsKeyValue(obj[key], denylist)) {
                return true;
            }
        }
    }
    return false;
}

// Build query filter from user input - implements the keyword restriction
function buildQueryFilter(userFilter, options) {
    const filter = {};
    
    // Apply the keyword denylist check
    const denylist = options.requestKeywordDenylist || config.requestKeywordDenylist;
    
    if (objectContainsKeyValue(userFilter, denylist)) {
        throw new Error('Query contains restricted keywords');
    }
    
    // Build the actual filter
    if (userFilter.name) {
        filter.name = userFilter.name;
    }
    if (userFilter.type) {
        filter.type = userFilter.type;
    }
    if (userFilter.restricted !== undefined) {
        filter.restricted = userFilter.restricted;
    }
    
    return filter;
}

// Webhook data processor endpoint for external integrations
app.post('/api/webhook/process', async (req, res) => {
    try {
        const { data, options } = req.body;
        
        if (!data) {
            return res.status(400).json({ error: 'Missing data payload' });
        }
        
        // Create a fresh options object for this request
        let requestOptions = {};
        
        // Merge user-provided options into request options
        if (options) {
            deepMerge(requestOptions, options);
        }
        
        const queryFilter = buildQueryFilter(data.filter || {}, requestOptions);
        
        const records = await DataRecord.find(queryFilter).limit(requestOptions.maxResults || config.maxResults);
        
        res.json({
            success: true,
            count: records.length,
            records: records.map(r => ({
                name: r.name,
                type: r.type,
                content: r.content
            }))
        });
        
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
});

// Standard data query endpoint
app.post('/api/process', async (req, res) => {
    try {
        const { filter } = req.body;
        
        // Check against denylist
        if (objectContainsKeyValue(filter || {}, config.requestKeywordDenylist)) {
            return res.status(403).json({ error: 'Query contains restricted keywords' });
        }
        
        const queryFilter = {};
        if (filter) {
            if (filter.name) queryFilter.name = filter.name;
            if (filter.type) queryFilter.type = filter.type;
        }
        
        // Only return non-restricted records via normal API
        queryFilter.restricted = false;
        
        const records = await DataRecord.find(queryFilter).limit(config.maxResults);
        
        res.json({
            success: true,
            count: records.length,
            records: records.map(r => ({
                name: r.name,
                type: r.type,
                content: r.content
            }))
        });
        
    } catch (error) {
        res.status(500).json({ error: 'Internal server error' });
    }
});

// List available record types
app.get('/api/types', async (req, res) => {
    try {
        const types = await DataRecord.distinct('type', { restricted: false });
        res.json({ types });
    } catch (error) {
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Home page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'templates', 'index.html'));
});

// Health check
app.get('/health', (req, res) => {
    res.json({ status: 'ok' });
});

// Error handling
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ error: 'Internal server error' });
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
