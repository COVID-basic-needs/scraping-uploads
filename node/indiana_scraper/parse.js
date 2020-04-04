const csv = require('csvtojson');
const fs = require('fs');
const shell = require('shelljs');
const csvjson = require('csvjson');
const time = require('./getDateTime.js');

// script that converts CSV file to JSON, formats the objects,
// then writes them to a file.
// Author -  Trevor O'Farrell

const formated_data = [];
const dateNow = time.getDateTimeNow();

const parseCsvToJson = (path) => {
  csv()
    .fromFile(path)
    .then((jsonObj) => {
      site_data = jsonObj;
      try {
        for (let i = 0; i <= site_data.length; i++) {
          let days = site_data[i].Days;
          if (String(site_data[i].Days).length < 9) {
            days = site_data[i].Days.split('').join(', ').replace('R', 'Th');
          }

          const adderess = `${site_data[i].Street}, ${site_data[i].City}, Indiana ${String(site_data[i]['Zip Code'])}`;
          const item = {
            sponsorName: site_data[i]['Sponsor Name'],
            siteName: site_data[i]['Site Name'],
            siteAddress: String(adderess),
            siteState: 'Indiana',
            contactPhone: String(site_data[i].ContactPhone).replace(/\D+/g, ''),
            contactEmail: site_data[i].Email,
            startDate: site_data[i]['Start Date'],
            endDate: site_data[i]['End Date'],
            daysofOperation: days,
            meals: site_data[i].Meals,
            lunchTime: site_data[i].Time,
            uploadNotes: site_data[i].Notes,
            _createdOn: dateNow,
            _updatedOn: dateNow,
          };

          formated_data.push(item);
        }
        console.log(formated_data);
      } catch (e) {}

      fs.stat('./indiana_data.json', (err) => {
        if (err) {
          shell.touch('./indiana_data.json');
        }
      });
      fs.writeFile('indiana_data.json', JSON.stringify(formated_data, null, 4), (err) => {
        if (err) return console.log(err);
      });

      fs.readFile('./indiana_data.json', 'utf-8', (err, fileContent) => {
        if (err) {
          throw new Error(err);
        }
        const csvData = csvjson.toCSV(fileContent, {
          headers: 'key',
        });
        fs.writeFile('./final_data.csv', csvData, (err) => {
          if (err) {
            throw new Error(err);
          }
          console.log('Success!');
        });
      });
    });
};


module.exports = {
  parseCsvToJson,
};
