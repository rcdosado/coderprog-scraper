# coderprog-scraper

coderprog.com multi-threaded web scraper (using [selectorlib](https://pypi.org/project/selectorlib/))


## scraper.py

Run `python scraper.py --help` for options

Add `--num_pages <INTEGER>` to set the number of pages starting from index page, defaults to 5

Add `--max_workers <INTEGER>` to set the number of threads to run, default is 3 worker threads

Add `--sleep_time <INTEGER>` to set the number of seconds to sleep for every `--when_pause` value

Add `--when_pause <INTEGER>` to set the when to sleep calculated as num_pages MOD when_pause

Add `--dump_file <TEXT>` to set the json file name where to save the output JSON scraped filed, defaults to `scraped_data.json` 

##  tests\test_parsers.py

Run `pytest tests\test_parsers.py` for testing the RegEx patterns used to extract data from the site

Run `pytest tests\test_scraper.py` for testing scraper.py

