module.exports = function(address) {
    if(address !== undefined) {
        let zipSearch = address.match(/WA [0-9][0-9][0-9][0-9][0-9]/gm);
        if( zipSearch !== null) {
            zip = zipSearch[0].match(/[0-9]/gm).join('');
            return zip;
        } 
    }
    return ''
}