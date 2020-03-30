import os
import re
import dateparser
import calendar
import requests
import pandas as pd
from dateutil import relativedelta
from algoliasearch.search_client import SearchClient
from dotenv import load_dotenv

load_dotenv()
GOOGLE_KEY = os.getenv('GOOGLE_KEY')
ALGOLIA_APP_ID = os.getenv('ALGOLIA_APP_ID')
ALGOLIA_KEY = os.getenv("ALGOLIA_KEY")

assert GOOGLE_KEY is not None, "Missing GOOGLE_KEY in .env"
assert ALGOLIA_APP_ID is not None, "Missing ALGOLIA_APP_ID key in .env"
assert ALGOLIA_KEY is not None, "Missing ALGOLIA_KEY in .env"

date_fmt = "%-m/%-d/%Y"  # m/d/YYYY
days_abbrev = ["M","T","W","Th","F","Sa","S"]

report_cols = ['siteName', 'siteStatus', 'siteAddress', 'siteState', 'siteZip', 'contactPhone',
               'startDate', 'endDate', 'daysofOperation', 'breakfastTime', 'lunchTime', 'snackTimeAM',
               'snackTimePM', 'dinnerSupperTime']


class ScrapingError(Exception):
    """json data url not found in html. Possible schema change."""


def georeference_address(address):
    url = 'https://maps.googleapis.com/maps/api/geocode/json'
    data = {
        'address': address,
        'key': GOOGLE_KEY
    }
    response = requests.get(url, params=data)

    if response.status_code != 200:
        return

    response = response.json()
    if not response['results']:
        return

    result = response['results'][0]  # assuming only 1 result for now
    return result['geometry']['location']


def dataframe_to_algolia(df):
    client = SearchClient.create(ALGOLIA_APP_ID, ALGOLIA_KEY)
    index = client.init_index('us_foodbank')

    records = []
    df = df.where(pd.notnull(df), '')
    for i, row in df.iterrows():
        record = {}
        for col in report_cols:
            record[col] = row[col]

        location = georeference_address(record['siteAddress'])
        if location is None:
            print('Could not geo reference location: ({0}, {1})'.format(record['siteName'], record['siteAddress']))
            continue

        record['_geoloc'] = location

        open_times = row['breakfastTime':'dinnerSupperTime'].tolist()
        open_times = [time for time in open_times if time]
        record['openTimes'] = ', '.join(open_times)

        records.append(record)

    index.save_objects(records, {'autoGenerateObjectIDIfNotExist': True})

def get_coords_from_google_map_url(url):
    d = {}
    coord_pattern = re.compile(r"3d(?P<latitude>\-?\d+\.\d+)\!4d(?P<longitude>\-?\d+\.\d+)")
    m = re.search(coord_pattern, url)
    if m:
        d = m.groupdict()
    return d

def clean_and_sort_days_list(days_of_op: ["T", "M", "W"]) -> "M,T,W":
    """removes any duplicates from list and orders them according to the days_abbrev"""

    capitalize = days_abbrev == [d.capitalize() for d in days_abbrev]
    # either capitalize the list or make it all upper

    if capitalize:
        days_of_op = [d.capitalize() for d in days_of_op]
    else:
        days_of_op = [d.upper() for d in days_of_op]

    days_of_op = list(set(days_of_op))
    try:
        days_of_op.sort(key=days_abbrev.index)
    except ValueError:
        # means day isn't in the abbrev, so just return it
        pass
    return ",".join(days_of_op)

def convert_start_end_dates(start_date: "March 3", end_date: "March 23") -> ("start datetime", "end datetime"):
    """convert start and end dates into datetime objects"""
    # check to see if end_date is missing numbers, if so, assume end of month
    try:
        int(end_date[-2:])
    except ValueError:
        # recreate the string using the end of month
        dt = dateparser.parse(end_date)
        if dt:
            day = calendar.monthrange(dt.year, dt.month)[1]
            end_date = "{} {}".format(end_date.strip(), day)

    # dateparser assumes current year for strings without years
    start = dateparser.parse(start_date)
    end = dateparser.parse(end_date)

    # check for 31 days when it should be 30 days
    if not start and start_date[-1] == '1':
        start = dateparser.parse(start_date[:-1] + "0")
    if not end and end_date[-1] == '1':
        end = dateparser.parse(end_date[:-1] + "0")

    if start_date:
        if end:
            # check if end is before the start since dateparser assumes current year
            # like start Nov 12 and end Jan 23
            if end <= start:
                end = end + relativedelta(years=1)
    return start, end


def extract_month_day_range(text: "March 23-26 or March 23-April 5") -> ("start datetime.obj", "end datetime.obj"):
    """convert date text range (March 23-26) into start and end datetime objects"""
    start = None
    end = None
    month_day_range_pattern = re.compile(
        r"(?P<start_month>[a-z]+)\s(?P<start_date>\d+)\s?\-\s?(?P<end_month>[a-z]+)?\s?(?P<end_date>\d+|(?:tbd))?",
        flags=re.I)

    m = re.search(month_day_range_pattern, text)
    if m:
        d = m.groupdict()
        if not d['end_month']:  # means days only
            # check to see if we can use start month
            if d['start_date'] > d['end_date']:
                print("error parsing %s . Start date appears to be greater than the end date.")
            else:
                d.update({'end_month': d['start_month']})
        # recreate the strings and send to
        start = "{start_month} {start_date}".format(**d).replace("None", "")
        end = "{end_month} {end_date}".format(**d).replace("None", "")
        #     return start, end

        start, end = convert_start_end_dates(start, end)
    return start, end


def extract_explict_days(text: "Lunch M,W,F") -> ["M", "W", "F"]:
    """Searches for day 1-2 character days of the weeks"""

    days_p = re.compile(r"(\b[a-z]{1,2})(?:\s|\-|\,|\b)", flags=re.I)
    days = re.findall(days_p, text) or []
    days = [d for d in days if d.lower() not in ["am", "pm"]]

    return days


def extract_weekday_range(text: "Monday-Wednesday or M-W") -> ["M", "T", "W"]:
    """Converts Monday-Wednesday and M-W into to M,T,W,Th,F,Sa,S format"""
    start_ix = None
    end_ix = None
    abbrevs = [d.lower() for d in days_abbrev]
    text = text.lower().strip()

    # this is the offset to add to the dateparser weekday index, it assumes M is 0
    dp_offset = abbrevs.index("m")

    p = re.compile(r"(\b[a-z]+)(?:\s?\-\s?)(\b[a-z]+)", flags=re.I)
    m = re.search(p, text)
    if m:
        start, end = m.groups()
    else:
        return

    start = start.strip()
    end = end.strip()

    # first check if the days is already in abbrevs
    if start in abbrevs:
        start_ix = abbrevs.index(start)
    if end in abbrevs:
        end_ix = abbrevs.index(end)

    # if not, try to convert the day using dateparser
    if start_ix is None:
        start_day = dateparser.parse(start)
        if start_day:
            # returns the index of the day of the week. Monday = 0
            start_ix = start_day.weekday() + dp_offset

    if end_ix is None:
        end_day = dateparser.parse(end)
        if end_day:
            end_ix = end_day.weekday() + dp_offset

    if start_ix is not None and end_ix is not None:
        abbrevs = days_abbrev * 2
        # check to see if dates are reversed as in Monday-Sunday
        if start_ix > end_ix:
            return abbrevs[start_ix:end_ix + 8]
        else:
            return abbrevs[start_ix:end_ix + 1]


def extract_meal_times(text: 'Breakfast: 7:30 AM - 9:00 AM; Lunch: 11:00 AM - 12:30 PM') -> {
    'breakfastTime': '7:30 AM - 9:00 AM', 'lunchTime': '11:00 AM - 12:30 PM'}:
    """Gets meals and times from string."""
    d = {}

    time_pattern = re.compile("(\w+)\:\s(\d{1,2}(?:\:\d{2})?\s*[A|P]M(?:\s*\-\s*\d{1,2}(?:\:\d{2})\s*[A|P]M)?)",
                              flags=re.I)
    matches = re.findall(time_pattern, text)

    for match in matches:
        meal, time = match
        time = time.upper()
        if re.search("breakfast", meal, flags=re.I):
            d['breakfastTime'] = time
        if re.search("lunch", meal, flags=re.I):
            d['lunchTime'] = time
        if re.search("snack", meal, flags=re.I):
            if time.find("AM") > -1:
                d['snackTimeAM'] = time
            if time.find("PM") > -1:
                d['snackTimePM'] = time

        if re.search("(?:supper)|(?:dinner)", meal, flags=re.I):
            d['dinnerSupperTime'] = time
    return d

def extract_weekday_range_or_weekdays(text: 'Breakfast M-Th') -> ["M", "T", "W", "Th"]:
    """Extracts day range like Monday-Sunday or M-W and also specific days like M,W,Th
    """
    # check for range first
    days = extract_weekday_range(text)
    if not days:
        days = extract_explict_days(text)
    return days
