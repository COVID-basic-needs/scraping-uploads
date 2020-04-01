const dbModel = [
  {
    siteName: 'A commonly recognized name for the food distribution site', // MANDATORY
    siteProvider: 'School District or Parent Organization',
    siteStatus: 'Open', // MANDATORY; one of​ 'Open​' or 'C​losed'
    siteAddress: '1234 Example Street, San Diego, CA 90210', // MANDATORY
    siteStreetAddress: '1234 Example Street',
    siteCity: 'San Diego',
    siteState: 'CA',
    siteZip: 90210,
    siteCountry: 'USA', // mailing-address style

    delivers: 't', // MANDATORY; one of 't' or 'f', used to flag 'call to arrange delivery' in message or frontend
    eligiblePopulations: 'Seniors, Families with Children, Youth', // if missing or length is 0 assume eligible to all
    description: 'Any extra details or notes', // TODO: decide character limit

    contactName: 'John Doe',
    contactEmail: 'email@site.org',
    contactPhone: 8001234567, // Phone number, formatted as a 10-digit string with no spaces or extra characters.
    url: 'https://site.org/', // website where updated information may be found

    startDate: '2016-04-21T20:00', // date in ISO 8601 format (YYYY-MM-DD), time optional
    endDate: '2020-04-21',

    // MANDATORY; schema.org/Google standard, timeslots in a week the site operates:
    // a comma-separated list of 2-letter week days (​Mo,Tu,We,Th,Fr,Sa,Su) followed by a space and
    // the time range in hypenated 24hr time; adjacent matching days' schedules may be combined by
    // hypenating the weekdays before the hours; multiple timeslots in a day must be comma-separated
    // and the weekday restated.
    openingHours: 'Mo-Fr 07:30-09:00, Mo-Fr 11:00-13:00, Tu 17:00-18:00, Th 17:00-18:00, Sa 09:00-12:00', // MANDATORY

    latitude: 37.75104109999999, // Site latitude and longitude in the WGS84/4326 coordinate system
    longitude: -122.4974065, // Needed to support uploaded flat file formats, i.e. csv & xlsx

    // ------------------------------------------------------------------
    // Below fields are not needed for incoming data or for No Kid Hungry CSV export,
    // they will be created upon upload for the Algolia database.
    // ------------------------------------------------------------------

    _geoloc: { // Algolia-style site lat/lng object, required for geoloc ordering
      lat: 37.75104109999999,
      lng: -122.4974065
    },
    eligibility: [ // if length is 0, assume eligible to all
      'Seniors',
      'Families with Children',
      'Youth'
    ],
    schedule: [ // note the transformation to combine hours on the same day previously separated in openingHours' comma-delineated values
      'Mo-Fr 07:30-09:00 11:00-13:00',
      'Tu 17:00-18:00',
      'Th 17:00-18:00',
      'Sa 09:00-12:00'
    ],
    dateCreated: '2020-04-21T20:00:00', // datetime in ISO 8601 format (YYYY-MM-DDThh:mm:ss)
    dateModified: '2020-04-21T20:00:00'
  }
];
