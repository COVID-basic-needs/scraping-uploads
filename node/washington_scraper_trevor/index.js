const puppeteer = require('puppeteer-extra');
const fs = require('fs');
const csvjson = require('csvjson');

// A puppeteer script to scrape data on school lunches/meals available
// in the state of washington. Data is collected from:
// https://www.esd113.org/family-services-map
// Author -  Trevor O'Farrell

async function scrape() {

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
            '--user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3312.0 Safari/537.36"',
        ],
        headless: false,
        });

        const page = (await browser.pages())[0];
        await page.setViewport({
            width: 800,
            height: 1800
        });

        await page.goto('https://www.esd113.org/family-services-map/')
        await page.waitForSelector('#popmake-6596 > button', { timeout: 4000 })
        await page.click('#popmake-6596 > button')

        function delay(time) {
            return new Promise(function(resolve) { 
                setTimeout(resolve, time)
            });
        }

        const returnPage = async function returnPage() {

            const location = await page.evaluate(() => {
                const locations = Array.from(document.querySelectorAll('td.column-location'))
                return locations.map((a) => a.textContent);
            })

            const address = await page.evaluate(() => {
                const locations = Array.from(document.querySelectorAll('td.column-address'))
                return locations.map((a) => a.textContent.replace(/['"]+/g, ''));
            })

            const hours = await page.evaluate(() => {
                const locations = Array.from(document.querySelectorAll('td.column-hours'))
                return locations.map((a) => a.textContent);
            })

            const foodType = await page.evaluate(() => {
                const locations = Array.from(document.querySelectorAll('td.column-type-of-food-service'))
                return locations.map((a) => a.textContent);
            })

            const website = await page.evaluate(() => {
                const locations = Array.from(document.querySelectorAll('td.column-website > a'))
                return locations.map((a) => a.href);
            })

            const info = await page.evaluate(() => {
                const locations = Array.from(document.querySelectorAll('td.column-other-information-if-necessary'))
                return locations.map((a) => a.textContent);
            })

            let item = {}
            const itemList = []
            for (let i = 0; i < 10; i++) {
                
                let food = String(foodType[i]).replace('/', ' or ')
                item = {
                    'location': location[i],
                    'address': address[i],
                    'hours': hours[i],
                    'foodType': food,
                    'website': website[i],
                    'info': info[i],
                }
                itemList.push(item)
            }
            return(itemList)
        }

        /*var pageCount = await page.evaluate(() => {
            let ret = document.querySelector('#table_1_paginate > span > a:nth-child(7)')
            return(ret)
        })

        console.log(pageCount.innerHTML)
        pageCount = Number(pageCount.innerHTML)*/
        
        const fullList = []
        for (let i = 0; i <= 125; i++) {
            let data = await returnPage()
            fullList.push(data)
            await page.click('#table_1_next')
            await delay(400)
        }

        fs.writeFile('washington_data.json', JSON.stringify(fullList, null, 4), (err) => {
            if (err) return console.log(err);
        });

        browser.close()

        fs.readFile('./washington_data.json', 'utf-8', (err, fileContent) => {
            if (err) {
              throw new Error(err);
            }

            const csvData = csvjson.toCSV(fileContent, {
              headers: 'key',
            });

            fs.writeFile('./washington_data.csv', csvData, (err) => {
              if (err) {
                throw new Error(err);
              }
              console.log('Success!');
            });
        });

    } catch (e) {
        console.error(e);
    }  

}

scrape()
