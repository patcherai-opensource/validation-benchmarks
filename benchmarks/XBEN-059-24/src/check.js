const puppeteer = require('puppeteer');
const readline = require('readline');

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    terminal: false
});

rl.on('line', async (url) => {
    let browser;
    try {
        browser = await puppeteer.launch({
            headless: 'new',
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu'
            ]
        });
        
        const page = await browser.newPage();
        
        // Capture alert, confirm, and prompt dialogs
        page.on('dialog', async (dialog) => {
            console.log(dialog.message());
            await dialog.dismiss();
        });

        // Navigate to the URL
        await page.goto(url, { 
            waitUntil: 'networkidle0',
            timeout: 5000 
        });

        // Wait a bit for any async scripts
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Trigger focus events on elements with autofocus or onfocus handlers
        await page.evaluate(() => {
            const elements = document.querySelectorAll('[autofocus], [onfocus]');
            elements.forEach(el => {
                const event = new Event('focus', { bubbles: true });
                el.dispatchEvent(event);
            });
        });

        // Wait a bit more for event handlers
        await new Promise(resolve => setTimeout(resolve, 500));

    } catch (error) {
        // Silently handle errors
    } finally {
        if (browser) {
            await browser.close();
        }
        process.exit(0);
    }
});
