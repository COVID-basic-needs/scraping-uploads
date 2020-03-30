import os
from scrapers.idaho import Idaho
from scrapers.ohio import Ohio
from scrapers.utils import report_cols, dicts_to_algolia

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

#scrapers_dict = {"ohio": Ohio, "idaho": Idaho}
scrapers_dict = {"ohio": Ohio}

def get_report_format_type():
    file_fmt = input("File type? [csv]/xlsx/json  ").strip().lower()
    file_fmt = file_fmt if file_fmt else "csv"
    if file_fmt not in ["csv","xlsx","json"]:
        return
    else:
        return file_fmt


def main():
    file_fmt = get_report_format_type()
    if not file_fmt:
        print("%s is not a valid option, try again")
        file_fmt = get_report_format_type()
    if not file_fmt:
        print("Incorrect again")
        exit()

    for state_name, scraper in scrapers_dict.items():
        if state_name == 'ohio':
            records = scraper.scrape()
            #dicts_to_algolia(records)
        else:
            df = scraper().scrape()
            if file_fmt == "xlsx":
                fn = os.path.join(DATA_DIR, f"{state_name}.xlsx")
                df[report_cols].to_excel(fn, index=False)
            elif file_fmt == "csv":
                fn = os.path.join(DATA_DIR, f"{state_name}.csv")
                df[report_cols].to_csv(fn, index=False)
            else:
                fn = os.path.join(DATA_DIR, f"{state_name}.json")
                df[report_cols].to_json(fn, orient="records")


if __name__ == "__main__":
    main()