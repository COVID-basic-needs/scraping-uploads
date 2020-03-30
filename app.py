import os
import argparse
from scrapers.idaho import Idaho
from scrapers.delaware import Delaware
from scrapers.utils import report_cols, dataframe_to_algolia

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

scrapers_dict = {"idaho": Idaho,
                 "delaware": Delaware}

def get_report_format_type():
    file_fmt = input("File type? [csv]/xlsx/json  ").strip().lower()
    file_fmt = file_fmt if file_fmt else "csv"
    if file_fmt not in ["csv","xlsx","json"]:
        return
    else:
        return file_fmt

def main():
    parser = argparse.ArgumentParser('State Web Scraper')
    parser.add_argument('-e', '--ext', help='Output extension', type=str, default='')
    args = parser.parse_args()

    for state_name, scraper in scrapers_dict.items():
        print("\n\n scraping %s now" % state_name)
        df = scraper().scrape()
        if args.ext == "xlsx":
            fn = os.path.join(DATA_DIR, f"{state_name}.xlsx")
            df[report_cols].to_excel(fn, index=False)
        elif args.ext == "csv":
            fn = os.path.join(DATA_DIR, f"{state_name}.csv")
            df[report_cols].to_csv(fn, index=False)
        elif args.ext == 'json':
            fn = os.path.join(DATA_DIR, f"{state_name}.json")
            df[report_cols].to_json(fn, orient="records")
        else:
            dataframe_to_algolia(df)


if __name__ == "__main__":
    main()