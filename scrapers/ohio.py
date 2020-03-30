import csv
import datetime
import json
import os
from algoliasearch.search_client import SearchClient
from scrapers.utils import georeference_address

FLAG_DO_GEOLOC = False # we get charged for these API calls - see local backup of previous run
FLAG_EXPORT_LOCAL = True

# original spreadsheet column headers:
#  0 Sponsor Name
#  1 IRN
#  2 Site Name
#  3 Site ID
#  4 Contact First Name
#  5 Contact Last Name
#  6 Contact Phone
#  7 Address Line 1
#  8 City
#  9 State
# 10 Zip
# 11 County
# 12 Start Date
# 13 Site Type
# 14 Breakfast Time
# 15 Breakfast Days
# 16 Lunch Time
# 17 Lunch Days
# 18 PM Snack Time
# 19 PM Snack Days
# 20 Prepared on Site
# 21 Transported to Site
# 22 Meal Time Extension

class Ohio:

    @classmethod
    def scrape(cls):
        records = []

        with open(os.path.join("raws", "ohio.csv"), 'rU') as csvFile:
            print("starting parsing for Ohio...")
            csvReader = csv.reader(csvFile, delimiter=',')

            # row is a list of strings
            for row in csvReader:
                #print(row)
                record = {}
                siteAddress = f'{row[7]}, OH {row[10]}'
                open_times = [row[14], row[16], row[18]]
                open_times = [time for time in open_times if time]
                open_times = ', '.join(open_times)

                location = ""
                if FLAG_DO_GEOLOC:
                    location = georeference_address(siteAddress)
                    if location is None:
                        print('Could not geo reference location: ({0}, {1})'.format(
                            row[2], siteAddress))
                        continue

                record['siteName'] = row[2]
                record['siteStatus'] = ""
                record['siteAddress'] = siteAddress
                record['siteAddress_json:'] = {
                    "streetAddress" : row[7],
                    "city" : row[8],
                    "state" : 'OH',
                    "zip" : row[10],
                };
                record['siteState'] = 'OH'
                record['siteZip'] = row[10]
                record['contactPhone'] = row[6]
                record['startDate'] = row[12]
                record['endDate'] = ""
                record['daysofOperation'] = Ohio.parseDaysOfOperation(row[15], row[17], row[19])
                record['breakfastTime'] = row[14]
                record['lunchTime'] = row[16]
                record['snackTimeAM'] = ""
                record['snackTimePM'] = row[18]
                record['dinnerSupperTime'] = ""
                record['openTimes'] = open_times
                record['_geoloc'] = location
                record['_createdOn'] = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                record['_updatedOn'] = ""

                records.append(record)

        if FLAG_EXPORT_LOCAL:
            print("writing to local file...")
            with open(os.path.join("data", "ohio_w_geoloc_backup.json"), 'w') as fout:
                json.dump(records, fout)
            print("local export done")

        return records

    # this will sometimes return a nested list, if days of week differ between breakfast, lunch, snack, etc.
    @staticmethod
    def parseDaysOfOperation(breakfastDays, lunchDays, pmSnackDays):
        combinedResults = []

        # simple case: only 1 identical set of days, across all types of meals
        if breakfastDays == lunchDays and (pmSnackDays == "" or pmSnackDays == breakfastDays):
            return Ohio.formatDaysOfWeek(breakfastDays)

        # other case: lists of lists
        if breakfastDays and breakfastDays != "":
            combinedResults.append(Ohio.formatDaysOfWeek(breakfastDays))
        if lunchDays and lunchDays != "":
            combinedResults.append(Ohio.formatDaysOfWeek(lunchDays))
        if pmSnackDays and pmSnackDays != "":
            combinedResults.append(Ohio.formatDaysOfWeek(pmSnackDays))
        return combinedResults

    # days_abbrev = ["M","T","W","Th","F","Sa","S"]
    @staticmethod
    def formatDaysOfWeek(strIn):
        splitList = str.split(strIn, ', ')
        copiedList = []
        for elem in splitList:
            if elem == 'Mon':
                copiedList.append('M')
            elif elem == 'Tue':
                copiedList.append('T')
            elif elem == 'Wed':
                copiedList.append('W')
            elif elem == 'Thu':
                copiedList.append('Th')
            elif elem == 'Fri':
                copiedList.append('F')
            elif elem == 'Sat':
                copiedList.append('Sa')
            elif elem == 'Sun':
                copiedList.append('S')
        return copiedList
