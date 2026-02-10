const express = require('express');
const { exec } = require('child_process');
const path = require('path');
const shellEscape = require('./lib/shellEscape');

const app = express();
const PORT = process.env.PORT || 80;

app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

app.get('/', (req, res) => {
    res.render('index');
});

app.get('/dns', (req, res) => {
    res.render('dns');
});

app.post('/api/dns', (req, res) => {
    const { domain, recordType } = req.body;
    
    if (!domain) {
        return res.status(400).json({ error: 'Domain is required' });
    }
    
    const validTypes = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA'];
    const type = validTypes.includes(recordType) ? recordType : 'A';
    
    const escapedDomain = shellEscape.escape(domain);
    
    const command = `dig +short ${escapedDomain} ${type}`;
    
    exec(command, { timeout: 10000 }, (error, stdout, stderr) => {
        if (error && error.killed) {
            return res.status(408).json({ error: 'Request timeout' });
        }
        
        const output = stdout || stderr || 'No records found';
        res.json({ 
            domain: domain,
            type: type,
            result: output.trim()
        });
    });
});

app.get('/whois', (req, res) => {
    res.render('whois');
});

app.post('/api/whois', (req, res) => {
    const { domain } = req.body;
    
    if (!domain) {
        return res.status(400).json({ error: 'Domain is required' });
    }
    
    const escapedDomain = shellEscape.escape(domain);
    
    const command = `whois ${escapedDomain} 2>/dev/null | head -50`;
    
    exec(command, { timeout: 15000 }, (error, stdout, stderr) => {
        if (error && error.killed) {
            return res.status(408).json({ error: 'Request timeout' });
        }
        
        const output = stdout || 'Unable to retrieve WHOIS information';
        res.json({
            domain: domain,
            result: output.trim()
        });
    });
});

app.get('/traceroute', (req, res) => {
    res.render('traceroute');
});

app.post('/api/traceroute', (req, res) => {
    const { host, maxHops } = req.body;
    
    if (!host) {
        return res.status(400).json({ error: 'Host is required' });
    }
    
    const hops = parseInt(maxHops) || 10;
    const safeHops = Math.min(Math.max(hops, 1), 15);
    
    const escapedHost = shellEscape.escape(host);
    
    const command = `traceroute -m ${safeHops} -w 2 ${escapedHost} 2>&1`;
    
    exec(command, { timeout: 30000 }, (error, stdout, stderr) => {
        if (error && error.killed) {
            return res.status(408).json({ error: 'Request timeout' });
        }
        
        const output = stdout || stderr || 'Traceroute failed';
        res.json({
            host: host,
            maxHops: safeHops,
            result: output.trim()
        });
    });
});

app.use((err, req, res, next) => {
    res.status(500).json({ error: 'Internal server error' });
});

app.use((req, res) => {
    res.status(404).send('Not Found');
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running on port ${PORT}`);
});
