import re
import json
import requests
from lxml import etree
import pandas as pd

from scrapers.utils import ScrapingError, extract_weekday_range, extract_month_day_range, extract_meal_times, extract_explict_days, clean_and_sort_days_list, extract_weekday_range_or_weekdays,days_abbrev, date_fmt, report_cols


class Idaho:
    def __init__(self):
        self.df = None
        self.new_cols = ['hasBreakfast', 'hasLunch', 'hasSnackAM', 'hasSnackPM', 'hasDinnerSupper']

    def scrape(self):
        print("scraping....")
        self.data = Scraper.scrape()
        print("loading data....")
        self.df = self._load_dataframe()
        self._add_columns()
        self._add_coordinates()
        print("processing data....")
        self._process_df()
        return self.df

    def _load_dataframe(self):
        df = pd.DataFrame(self.data['dataRS'], columns=self.data['columnNames'])
        col_map = {'Meal Service Address': 'siteAddress',
                   'City': 'siteCity',
                   'State': 'siteState',
                   'Zipcode': 'siteZip',
                   'Name of Meal Service Location': 'siteName',
                   'Phone Number': 'contactPhone',
                   'Type of Meals Served': 'mealTypes',
                   'Service Dates': 'serviceDates'
                   }
        df.columns = df.columns.map(col_map)
        self.df = df
        return df

    def _add_columns(self):
        for col in self.new_cols + report_cols:
            if col not in self.df.columns:
                self.df[col] = None

    def _add_coordinates(self):
        coords = pd.DataFrame(self.data['mapRS'])
        # make sure the address from the coords maps to the address on the df
        coords.a = coords.a.str.strip()
        self.df.siteAddress = self.df.siteAddress.str.strip()
        if sum(self.df.siteAddress != coords.a) == 0:
            self.df['latitude'] = coords['lt']
            self.df['longitude'] = coords['ln']
            print("succesfully added coordinates")
        else:
            print("error in loading coordinates, addresses from map data do not match.\
                          Coords have not been added.")

    def _process_df(self):
        self.df = self.df.apply(SiteDetails.process_df_row, axis=1)
        self.df = self.df.apply(MealTypes.process_df_row, axis=1)
        self.df = self.df.apply(ServiceDates.process_df_row, axis=1)
        self.df.startDate = self.df.startDate.dt.strftime(date_fmt)
        self.df.endDate = self.df.endDate.dt.strftime(date_fmt)

        # set empty days to None
        ix = self.df.daysofOperation.str.strip() == ""
        self.df.loc[ix, 'daysofOperation'] = None


class Scraper:
    URL = 'https://batchgeo.com/map/3195baf394a7f7db04ce06c69b17842f'

    @classmethod
    def scrape(cls):
        html = cls.make_request(cls.URL)
        json_url = cls._find_json_url(html)
        if not json_url:
            raise ScrapingError()

        script_data = cls.make_request(json_url)
        return cls._load_as_json_data(script_data)

    def make_request(url):
        headers = {
            'authority': 'batchgeo.com',
            'cache-control': 'max-age=0',
            'dnt': '1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
            'sec-fetch-dest': 'document',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'accept-language': 'en-US,en;q=0.9',
        }

        r = requests.get(url, headers=headers)
        r.raise_for_status()
        return r.text

    @staticmethod
    def _load_as_json_data(text):
        skip_chars = "per = "
        n = len(skip_chars)
        data = json.loads(text[n:-1])
        return data

    @staticmethod
    def _find_json_url(html):
        tree = etree.HTML(html)
        src_url = tree.xpath(".//script[contains(@src,'map/json')]")
        if src_url is not None:
            src_url = src_url[0]
            src_url = src_url.get('src')
            # check if it just needs http
            if src_url.startswith("//"):
                src_url = "https:" + src_url
            # check if it's a relative path
            elif src_url.startswith("/"):
                src_url = "https://batchgeo.com" + src_url
        return src_url


class MealTypes:
    """Breakfast: 7:30 AM - 9:00 AM; Lunch: 11 """

    @classmethod
    def process_df_row(cls, row):
        d = cls.extract_meal_times(row['mealTypes'])

        days_of_op = row['daysofOperation']
        days_of_op = days_of_op.split(",") if days_of_op else []

        for k, v in d.items():
            if k == "daysofOperation" and days_of_op:
                days_of_op.extend(row['daysofOperation'])
            else:
                row[k] = v
        if days_of_op:
            row['daysofOperation'] = clean_and_sort_days_list(days_of_op)
        return row

    @classmethod
    def extract_meal_times(cls, text: 'Breakfast: 7:30 AM - 9:00 AM; Lunch: 11:00 AM - 12:30 PM') -> {
        "breakfastTime": "7:30 AM - 9:00 AM", "Lunch": "11:00 AM - 12:30 PM"}:
        d = {}
        text = text.lower()

        # if it has times, they're split like
        # Breakfast: 7:30 AM - 9:00 AM; Lunch: 11 AM - 12:30 PM
        meal_times = extract_meal_times(text)
        if meal_times:
            d.update(meal_times)

        if re.search("breakfast", text, flags=re.I):
            d['hasBreakfast'] = True
        if re.search("lunch", text, flags=re.I):
            d['hasLunch'] = True
        if re.search("(?:supper)|(?:dinner)", text, flags=re.I):
            d['hasDinnerSupper'] = True
        if re.search("snack", text, flags=re.I):
            # check if snack comes before or after lunch in the string
            if text.find("snack") > text.find("lunch"):
                d['hasSnackPM'] = True
            else:
                d['hasSnackAM'] = True

        days_of_op = extract_weekday_range_or_weekdays(text)
        if days_of_op:
            d['daysofOperation'] = clean_and_sort_days_list(days_of_op)

        return d


class ServiceDates:

    @classmethod
    def process_df_row(cls, row):
        """updates df row for values serviceDates"""
        start_dates = []
        end_dates = []
        days_of_op = row['daysofOperation']
        days_of_op = days_of_op.split(",") if days_of_op else []

        date_text = row['serviceDates']
        date_text = date_text.replace("\xa0", " ")

        # check for multiple dates split by ;
        splits = date_text.split(";")
        for split in splits:
            d = cls.extract_service_dates(split)
            if d.get("daysofOperation", []):
                days_of_op.extend(d.get('daysofOperation'))
            if d.get('startDate'):
                start_dates.append(d.get('startDate'))
            if d.get('endDate'):
                end_dates.append(d.get('endDate'))

        row['startDate'] = min(start_dates) if start_dates else None
        row['endDate'] = max(end_dates) if end_dates else None
        row['daysofOperation'] = clean_and_sort_days_list(days_of_op)

        return row

    @classmethod
    def extract_service_dates(cls, date_text: 'March 23 - March 26; April 6 - May (Monday-Thursday)') -> {}:
        d = {}

        dates_p = re.compile(r"(?P<start>\w+\s\d{1,2})\s?\-\s?(?P<end>\w+\s\d*)(?:\s?\((?P<days>\w+\s?\-\s?\w+)\))?")

        # check for dates like March 20-23
        d['startDate'], d['endDate'] = extract_month_day_range(date_text)
        d['daysofOperation'] = extract_weekday_range(date_text)

        return d


class SiteDetails:

    @classmethod
    def process_df_row(cls, row):
        row = cls._create_address(row)
        row = cls._clean_phone(row)
        return row

    @staticmethod
    def _create_address(row):
        row['siteAddress'] = f"{row['siteAddress']} {row['siteCity']}, {row['siteState']} {row['siteZip']}"
        return row

    @staticmethod
    def _clean_phone(row):
        row['contactPhone'] = "".join(re.findall("\d", row['contactPhone']))
        return row
