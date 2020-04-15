module.exports = function(string) {
    let noDays = string.replace(/([A-Z]|[a-z]){1,2}-([A-Z]|[a-z]){1,2}/gm, "").trim();
    return noDays;
}