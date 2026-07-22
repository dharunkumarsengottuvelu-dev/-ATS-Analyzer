const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  
  page.on('console', msg => console.log('BROWSER_CONSOLE:', msg.text()));
  page.on('pageerror', error => console.log('BROWSER_PAGEERROR:', error.message));
  page.on('requestfailed', request => console.log('BROWSER_REQUESTFAILED:', request.url(), request.failure().errorText));
  
  await page.goto('http://127.0.0.1:3000', { waitUntil: 'networkidle0' });
  
  await new Promise(r => setTimeout(r, 2000));
  
  const html = await page.content();
  console.log('HTML_LENGTH:', html.length);
  
  await browser.close();
})();
