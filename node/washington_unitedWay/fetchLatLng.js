const got = require('got');
const delay = require('delay');
const parser = require('parse-address'); // US Address parser

module.exports = async function(rawAddressString, cityName) {
    let parsedAddress = parser.parseLocation(rawAddressString)
    if( parsedAddress !== null ) {
        if( parsedAddress.street !== undefined && parsedAddress.number !== undefined) {
            let filteredStreet = parsedAddress.street.replace(' ','%20');
            let filteredCity = parsedAddress.city ? parsedAddress.city.replace(' ', '%20') : cityName.replace(' ', '%20');
            await delay(20); // Delay needed to adhere to Google API Rate Limit of 50 RPS
            let url = `https://maps.googleapis.com/maps/api/geocode/json?address=${filteredStreet},${filteredCity},WA&key=${process.env.GOOGLE_API_KEY}`
            let body = await got(url).json(); 
            
            if( body.results.length === 1 ) {
                let LatLng = {};
                LatLng.lat = body.results[0].geometry.location.lat;
                LatLng.lng = body.results[0].geometry.location.lng;
                return LatLng;
            } 
        } 
    }
    return {};
}