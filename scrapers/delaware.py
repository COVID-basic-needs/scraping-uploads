import requests
import dateparser
import pandas as pd
from bs4 import BeautifulSoup

from scrapers.utils import extract_weekday_range_or_weekdays, get_coords_from_google_map_url, date_fmt, report_cols

class Delaware:
    def __init__(self):
        self.df = None
        self.new_cols = ['hasBreakfast', 'hasLunch', 'hasSnackAM', 'hasSnackPM', 'hasDinnerSupper']

    def scrape(self):
        print("scraping....")
        html = self.make_request()
        self.soup = BeautifulSoup(html)
        print("loading data....")
        self.df = self._load_dataframe()
        print("processing data....")
        self._process_df()
        return self.df

    def make_request(url):
        headers = {
            'authority': 'www.doe.k12.de.us',
            'cache-control': 'max-age=0',
            'dnt': '1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
            'sec-fetch-dest': 'document',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'accept-language': 'en-US,en;q=0.9',
        }

        r = requests.get('https://www.doe.k12.de.us/page/4149', headers=headers)
        r.raise_for_status()

        return r.text

    def _load_dataframe(self):
        data = []

        table = self.soup.find("table", {"id": "mealTable"})

        thead = table.find("thead")
        cols = [x.text for x in thead.findAll("th")]
        for row in table.findAll("tr")[1:]:
            values = [td.text for td in row.findAll("td")]
            d = dict(zip(cols, values))

            a = row.find("a")
            if a:
                url = a.get("href")
                coords = get_coords_from_google_map_url(url)
                d.update(coords)
            data.append(d)

        return pd.DataFrame(data)

    def _process_df(self):
        self._update_df_column_names()
        self._update_df_days_of_op()
        self._add_df_columns()
        self._update_df_address()
        self._update_df_dates()
        # set empty days to None
        ix = self.df.daysofOperation.str.strip() == ""
        self.df.loc[ix, 'daysofOperation'] = None

    def _update_df_dates(self):
        def convert_date(text):
            if isinstance(text, str):
                dt = dateparser.parse(text)
                if dt:
                    return dt.strftime(date_fmt)
                else:
                    return text
            else:
                print("text is ", text)

        self.df.startDate = self.df.startDate.apply(convert_date)

    def _update_df_column_names(self):
        col_map = {'City': 'siteCity',
                   'Sponsor Name': 'siteSponsor',
                   'Site Name': 'siteName',
                   'Address': 'siteAddress',
                   'Zip': 'siteZip',
                   'County': 'siteCounty',
                   'Start Date': 'startDate',
                   'Breakfast Time': 'breakfastTime',
                   'Lunch Time': 'lunchTime',
                   'Days of Operation': 'daysofOperation'}

        self.df.columns = [col_map.get(x, x) for x in self.df.columns]

    def _add_df_columns(self):
        for col in report_cols:
            if col not in self.df.columns:
                self.df[col] = None

    def _update_df_days_of_op(self):
        self.df.daysofOperation = self.df.daysofOperation.apply(
            lambda x: ",".join(extract_weekday_range_or_weekdays(x)))

    def _update_df_address(self):
        self.df['siteState'] = "DE"

        def create_address(row):
            row['siteAddress'] = f"{row['siteAddress']} {row['siteCity']}, {row['siteState']} {row['siteZip']}"
            return row

        self.df.siteAddress = self.df.apply(create_address, axis=1)