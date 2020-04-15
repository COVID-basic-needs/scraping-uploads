const fetchZip = require('./fetchZip.js');
const parser = require('parse-address'); // US Address parser

module.exports = async function(rawAddressString, cityName) {
    let parsedAddress = parser.parseLocation(rawAddressString)
    let finalAddressString;
    if( parsedAddress !== null ) {
        if( parsedAddress.zip === undefined && parsedAddress.street !== undefined && parsedAddress.number !== undefined) {
            parsedAddress.zip = await fetchZip( parsedAddress.street, parsedAddress.city || cityName )
        } 
        finalAddressString = `${parsedAddress.number} ${parsedAddress.street} ${parsedAddress.type}, ${parsedAddress.city || cityName}, WA ${parsedAddress.zip}`
    } else {
        return rawAddressString;
    }

    return finalAddressString;
}