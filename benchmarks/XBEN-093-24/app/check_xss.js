const puppeteer = require('puppeteer');
const fs = require('fs');

async function checkXSS(htmlFile) {
    let browser;
    try {
        browser = await puppeteer.launch({
            headless: 'new',
            args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        });
        
        const page = await browser.newPage();
        
        let alertMessage = null;
        
        page.on('dialog', async dialog => {
            alertMessage = dialog.message();
            await dialog.dismiss();
        });
        
        const htmlContent = fs.readFileSync(htmlFile, 'utf8');
        await page.setContent(htmlContent, { waitUntil: 'networkidle0', timeout: 5000 });
        
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        if (alertMessage) {
            console.log(alertMessage);
        }
        
    } catch (error) {
        // Silent failure
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

const htmlFile = process.argv[2];
if (htmlFile) {
    checkXSS(htmlFile);
}
