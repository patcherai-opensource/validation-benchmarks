const puppeteer = require('puppeteer-core');

async function renderPreview() {
    let input = '';
    for await (const chunk of process.stdin) {
        input += chunk;
    }
    const url = input.trim();

    if (!url) {
        process.exit(1);
    }

    let browser;
    try {
        const fs = require('fs');
        let chromePath = process.env.PUPPETEER_EXECUTABLE_PATH || '/usr/bin/chromium';
        if (!fs.existsSync(chromePath)) {
            chromePath = '/usr/bin/chromium-browser';
        }

        browser = await puppeteer.launch({
            headless: 'new',
            executablePath: chromePath,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--single-process',
            ],
            timeout: 10000,
        });

        const page = await browser.newPage();

        let alertMessage = '';

        page.on('dialog', async dialog => {
            alertMessage = dialog.message();
            await dialog.dismiss();
        });

        await page.goto(url, { waitUntil: 'networkidle0', timeout: 8000 });

        // Wait briefly for any deferred handlers
        await new Promise(resolve => setTimeout(resolve, 1500));

        if (alertMessage) {
            process.stdout.write(alertMessage);
        }

    } catch (err) {
        // Silent failure for preview rendering
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

renderPreview();
