#!/usr/bin/python3

import requests
import urllib.request
import time
from bs4 import BeautifulSoup
import os.path, time
import csv
from correctresults import fix_inconsistencies

url = 'https://www.uwkc.org/free-meals-during-school-closures/'
response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
soup = BeautifulSoup(response.content, 'lxml')

# parse data from site

blocks = soup.find_all('div', {'class': 'accordion'})
results = []
for block in blocks:
    meal_info = block.find_all('p')
    for info in meal_info:
        county = block.find_previous_sibling('h2').text
        district_parent = info.find_parent('div', {'class': 'accordion_item'})
        district = district_parent.find('h3').text
        specs = info.text.split('\n')
        infolength = len(specs)
        
        if infolength < 2:
            continue
        
        if 'ROUTE' in specs[0] or 'Nutrition Delivery' in specs[0]:
            route = specs[0]
            for i in range(1, infolength - 1):
                skip = ['Yellow Camp (1', '1:30 – 11:45 AM)']
                if specs[i] in skip:
                    continue
                specs[i] = specs[i].strip(')')
                specs[i] = specs[i].split('(')
                locations = {
                    'siteName':route,
                    'siteStatus': '',
                    'siteAddress':specs[i][0],
                    'siteState':'WA',
                    'siteZip': '',
                    'siteCounty': county,
                    'contactPhone': '',
                    'startDate': '',
                    'endDate': '',
                    'daysofOperation': 'M, T, W, Th, F',
                    'siteTime': specs[i][1],
                    'breakfastTime': '',
                    'lunchTime': '',
                    'snackTimeAM': '',
                    'snackTimePM': '',
                    'dinnerSupperTime': '',
                    '_updatedOn': time.ctime(os.path.getmtime('washington_scraper.py')),
                }
                results.append(locations)
        else:
                
            locations = {
                'siteName':specs[0],
                'siteStatus': '',
                'siteState':'WA',
                'siteZip': '',
                'siteDistrict': district,
                'siteCounty': county,
                'contactPhone': '',
                'startDate': '',
                'endDate': '',
                'daysofOperation': '',
                'siteTime':specs[1],
                'breakfastTime': '',
                'lunchTime': '',
                'snackTimeAM': '',
                'snackTimePM': '',
                'dinnerSupperTime': '',
                '_updatedOn': time.ctime(os.path.getmtime('washington_scraper.py')),
            }

            if infolength > 2:
                locations['siteTime']=specs[2]
                locations['siteAddress']=specs[1]
            results.append(locations)


def siteTime_format(entry, dayandtime):
    # separates date and time
    # takes into account range denoted by ' - ' and '&'
    days = ['M', 'T', 'W', 'TH', 'F', 'Sa', 'Su']

    if dayandtime is None or dayandtime is '':
        return
    
    elif '&' in dayandtime:
        dayandtime = dayandtime.replace('&', ',')
        dayandtime = dayandtime.split(' ')
        opdays = []
        entry['daysofOperation'] = dayandtime[0]
        entry['siteTime'] = dayandtime[1]

    elif dayandtime[1] is ',':
        dayandtime =  dayandtime.split(' ')
        entry['daysofOperation'] = dayandtime[0]
        entry['siteTime'] = dayandtime[1]

    elif dayandtime[1] is not ',' and dayandtime[1] is '-':
        dayandtime = dayandtime.split(' ', 1)
        entry['siteTime'] = dayandtime[1]
        opdays = str(dayandtime[0])
        operationdays = []

        for i in range(0, len(days)):
            if opdays[0] == days[i]:
                while i < len(days) and days[i] != opdays[2]:
                    operationdays.append(days[i])
                    i+=1
                operationdays.append(days[i])
                entry['daysofOperation'] = (str(operationdays)).strip('][')

    elif dayandtime[0].isalpha() and (dayandtime[1] is ' ' or dayandtime[2] is ' '):
        dayandtime = dayandtime.split(' ')
        entry['daysofOperation'] = dayandtime[0]
        entry['siteTime'] = dayandtime[1]
                
# Manually fixing mutliple specific entries due to inconsistent formatting between entries
# via fix_inconsistencies function

fix_inconsistencies(results)

# format date and time per entry 

for entry in results:
    siteTime_format(entry, entry['siteTime'])

def save_to_csv(results):
    # save to csv file
    
    # grab fieldnames in same order as model
    '''
    fieldnames = []
    for fields in results[0].keys():
        fieldnames.append(fields)
    '''

    # grab fieldnames in accordance to most available data 
    fieldnames = ['siteName', 'siteTime',  'siteAddress', 'daysofOperation', 'siteDistrict', 'siteCounty',
                  'siteState', 'siteZip', 'contactPhone', 'startDate', 'breakfastTime','lunchTime',
                  'snackTimeAM', 'snackTimePM', 'dinnerSupperTime', 'siteStatus', 'endDate', '_updatedOn'] 

    with open('washington_1.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)

save_to_csv(results)

