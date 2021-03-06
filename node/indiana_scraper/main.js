const fs = require('fs');
const shell = require('shelljs');
const scraper = require('./googleSheetScraper.js');
const parse = require('./parse.js');

const filePath = './new_data.csv';

// reads the CSV download of the google doc:
// SFSP and SSO Meal Service Sites during COVID19 School Closures, IN
// https://docs.google.com/spreadsheets/d/1rG9WrIGhDkriNxL7sZFYM9VZ945IXyyNEKx_WV8UWV8/edit#gid=0
// and converts it to JSON complient to the V1 schema
// Author -  Trevor O'Farrell

async function scrapeIndiana() {
  try {
    // call puppeteer scraper to download CSV file from the google sheet
    await scraper.downloadCSV();
  } catch (e) {
    console.error(e);
  }

  fs.stat('./data.csv', (err) => {
    if (err) {
      console.log('no file');
      shell.touch('./data.csv');
    } else {
      // file exists
      fs.readFile('./data.csv', (e, data) => {
        if (e) {
          console.error(e);
          return;
        }
        // remove the first lines before the column names of the CSV file
        const linesExceptFirst = String(data).split('\n').slice(2).join('\n');
        fs.writeFileSync(filePath, linesExceptFirst);
      });
    }
  });
  // convert CSV to JSON, and format its structure + add keys

  fs.stat('./new_data.csv', (e) => {
    if (e) {
      shell.touch('./new_data.csv');
    }
    parse.parseCsvToJson(filePath);
  });
}

scrapeIndiana();
