let daysOfWeek = ['M','T','W','TH','F','SA','SU'] 

module.exports = function(string) {
    if(string === undefined) return false;
    if( string.match(/([A-Z]|[a-z]){1,2}-([A-Z]|[a-z]){1,2}/gm) !== null ) {
        let startDay = string.match(/([A-Z]|[a-z]){1,2}-([A-Z]|[a-z]){1,2}/gm)[0].match(/([A-Z]|[a-z]){1,2}-/gm)[0];
        startDay = startDay.slice(0,startDay.length-1);
        let endDay = string.match(/([A-Z]|[a-z]){1,2}-([A-Z]|[a-z]){1,2}/gm)[0].match(/-([A-Z]|[a-z]){1,2}/gm)[0].slice(1).toUpperCase();
        let days = [];
        for( let i = daysOfWeek.indexOf(startDay); i % daysOfWeek.length != daysOfWeek.indexOf(endDay); i++ ) days.push(daysOfWeek[i % daysOfWeek.length]);
        return days.toString();
    }
    return 'M,T,W,TH,F';
}