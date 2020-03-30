const dbModel = [
  {
    siteName: 'A commonly recognized name for the food distribution site.',
    siteStatus: 'Open', // Status of the food distribution site, one of​ Open​ or C​losed.
    siteAddress: {
      streetAddress: '1234 example street',
      city: '',
      state: '',
      zip: 90210
    },
    siteState: 'CA',
    siteZip: 90210, // i don't know why we need this if we have lat/lng - Max
    contactPhone: 8001234567, // Phone number, formatted as a 10-digit string with no spaces or extra characters.
    startDate: 'mm/dd/yy', // Date the site opens in the format ​mm/dd/yy.
    endDate: 'mm/dd/yy', // Date the site closes in the format ​mm/dd/yy.
    daysofOperation: '', // Days of the week the site operates. This is a comma-separated list of week day abbreviations i.e. ​M,T,W,Th,F,Sa,S.
    breakfastTime: '', // Time range breakfast is being served i.e. 7​ :45 AM- 8:30 AM​.
    lunchTime: '', // Time range lunch is being served i.e. ​11:40 AM- 12:30 PM.
    snackTimeAM: '', // Time range morning snacks are being served i.e. ​10:00 AM- 11:00 AM.
    snackTimePM: '', // Time range afternoon snacks are being served i.e. 3​ :30 PM- 4:30 PM​.
    dinnerSupperTime: '', // Time range dinner/supper is being served i.e. 5​ :00 PM- 8:00 PM​.

    // Below fields are not for No Kid Hungry CSV export, just for the database & Algolia.

    _geoloc: { // Site latitude and longitude in the WGS84/4326 coordinate system.
      lat: 37.75104109999999,
      lng: -122.4974065
    },
    _createdOn: '', // Timestamp of database entry creation. This will be in the format ​mm/dd/yy HH:MM:SS.
    _updatedOn: '' // Timestamp of most recent database entry update. This will be in the format ​mm/dd/yy HH:MM:SS​.
  }
];
