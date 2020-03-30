import datetime

from scrapers.utils import convert_start_end_dates, extract_explict_days, extract_meal_times, extract_month_day_range, extract_weekday_range, clean_and_sort_days_list

tests_clean_and_sort_days_list = [
    (["T","M","S"],["M","T","S"]),
    (["T","T","S"],["T","S"]),
    (["S","M","S"],["M","S"]),
]
for test in tests_clean_and_sort_days_list:
    result = clean_and_sort_days_list(test[0])
    assert result == test[1]


test_dict = {
    "March 23-26": [datetime.datetime(2020, 3, 23),datetime.datetime(2020, 3, 26)],
    "March 23-April 26": [datetime.datetime(2020, 3, 23),datetime.datetime(2020, 4, 26)],
    "Jan 23-April 26": [datetime.datetime(2020, 1, 23),datetime.datetime(2020, 4, 26)],
    "Dec 23-April 26": [datetime.datetime(2020, 12, 23),datetime.datetime(2021, 4, 26)],
}

for k,v in test_dict.items():
    dates = extract_month_day_range(k)
    assert dates[0] == v[0]
    assert dates[1] == v[1]