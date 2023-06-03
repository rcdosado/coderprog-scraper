# coderprog-scraper

coderprog.com multi-threaded web scraper (using [selectorlib](https://pypi.org/project/selectorlib/))


## scraper.py

Running  `python scraper.py` will use default values, these settings will : scrape first 5 pages from index page, using 3 worker threads, sleeping for 7 seconds every 5th page scraped, dumping the scraped data to scraped_data.json, the dump file is a list of python dictionaries, every item contain a resource which is either a book or a course

Replace `start_scrape()` with  `single_site_scrape_test("https://coderprog.com", "__output__.json")` to scrape single page for scraping single page JSON file


### options
Run `python scraper.py --help` for options

Add `--num_pages <INTEGER>` to set the number of pages starting from index page, defaults to 5

Add `--max_workers <INTEGER>` to set the number of threads to run, default is 3 worker threads

Add `--sleep_time <INTEGER>` to set the number of seconds to sleep for every `--when_pause` value

Add `--when_pause <INTEGER>` to set the when to sleep calculated as num_pages MOD when_pause

Add `--dump_file <TEXT>` to set the filename of the scraped file defaults to `scraped_data.json` in the current directory

## Running tests

Run `pytest tests\test_parsers.py` for testing the RegEx patterns used to extract data from the site

Run `pytest tests\test_scraper.py` for testing scraper.py

## Webscraper Features

Multithreading - every URL will be executed by a thread, and then saved one by one, so expect data to be saved in random order, but sure will be fast. unfortunately the site has some anti-scraping mechanism so a system sleep is needed. 

Memory efficient - every page JSON output is written in append mode to the dump file, every time page data is written to file, it is then release in memory. 

Regex pattern heuristics - resource attribute is parse not basing on the order in the html file, but by its text pattern. so it is basically guessing a token of text to determine its field, this is designed since resources is a mix of a book and a course. 

