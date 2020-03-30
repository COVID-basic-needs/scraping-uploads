from scrapers.ohio import Ohio

# This script is the entry point for the following other parts of the project:
# - Ohio
# - more to be added later?

# I separated this from app.py, the main entry point, because my implementation
# for Ohio does not use dataframes.

Ohio.scrape()
# dicts_to_algolia(records)
