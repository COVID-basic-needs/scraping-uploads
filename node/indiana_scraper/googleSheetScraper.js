const puppeteer = require('puppeteer-extra');

// A puppeteer script to download csv file from google spreadsheets, cannot use googlesheets 
// API due to the sheet not being published.
// Author -  Trevor O'Farrell

async function downloadCSV() {
    try {
      const browser = await puppeteer.launch({
        executablePath: '/usr/bin/google-chrome-stable',
        args: [
          '--incognito',
          '--no-sandbox',
          '--disable-setuid-sandbox',
          '--disable-infobars',
          '--ignore-certifcate-errors',
          '--ignore-certifcate-errors-spki-list',
          '--user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3312.0 Safari/537.36"'
        ],
        headless: true,
      })
      const context = await browser.newPage
      const page = (await browser.pages())[0]
      await page._client.send('Page.setDownloadBehavior', {behavior: 'allow', downloadPath: './'});

      console.log('Starting download.....')
      await new Promise(async (resolve) => {
        setTimeout(resolve, 3200);
        try {
            await page.goto('http://docs.google.com/spreadsheets/d/1rG9WrIGhDkriNxL7sZFYM9VZ945IXyyNEKx_WV8UWV8/gviz/tq?tqx=out:csv')
            resolve();
        } catch (err) {
            // encountering a bug after using page.goto() to the google spread sheets download link
            // so im using a timer to kill the promise, as the file has already been downloaded
            // but the promise will continue to wait, and the page/browser cant be closed using browser.close() or page.close()
            console.log('unhandled promise rejection handled!');
        }
      })
      .then(() => page.close());
  
      console.log('downloaded')
      browser.close()
    } catch(e) {}
  }

  
module.exports = {
    downloadCSV
}