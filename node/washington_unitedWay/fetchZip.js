const got = require('got');
const delay = require('delay');

module.exports = async function(street, city) {
    let filteredStreet = street.replace(' ','%20');
    let filteredCity = city.replace(' ', '%20');
    await delay(20); // Delay needed to adhere to Google API Rate Limit of 50 RPS
    let url = `https://maps.googleapis.com/maps/api/geocode/json?address=${filteredStreet},${filteredCity},WA&key=${process.env.GOOGLE_API_KEY}`
    let body = await got(url).json(); 
    let zip = '';
 
    if( body.results.length === 1 ) {
        let zipSearch = body.results[0].formatted_address.match(/WA [0-9][0-9][0-9][0-9][0-9]/gm);
        if( zipSearch !== null) {
            zip = zipSearch[0].match(/[0-9]/gm).join('');
        }
    } 
    return zip;
}