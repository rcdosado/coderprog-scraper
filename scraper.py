import os
import click
import datetime

import time
import requests
import json
import threading

from charset_normalizer import detect


from selectorlib import selectorlib
from selectorlib import formatter
from parsers.book_parser import parse_book_metadata
from parsers.course_parser import parse_course_metadata

from parsers.utils import (
    read_file_content,
    save_text,
    save_json,
)

ROOT_URL = "https://coderprog.com"

import concurrent.futures


def read_selector_file(filename):
    cur_dir = os.path.dirname(__file__)
    with open(os.path.join(cur_dir, filename)) as fileobj:
        content = fileobj.read()
    return content


def get_headers():
    # Creating headers.
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        #  'accept-encoding': 'gzip, deflate, sdch, br',
        "accept-language": "en-GB,en;q=0.8,en-US;q=0.6,ml;q=0.4",
        "cache-control": "max-age=0",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36",
    }
    return headers


# base site e.g https://coderprog.com
def _link_generator(pages):
    yield ROOT_URL
    for i in range(2, pages + 1):
        yield ROOT_URL + "/page/{}/".format(i)


def get_response(url):
    response = requests.get(url, verify=True, headers=get_headers())
    if response.status_code != 200:
        print("URL request to {} returns ERROR {}: ".format(url, response.status_code))
        return None
    else:
        return response.text


def html_to_json(html):
    try:
        formatters = formatter.Formatter.get_all()
        extractor = selectorlib.Extractor.from_yaml_string(
            read_selector_file("selector_file.yml"), formatters=formatters
        )
        json_data = extractor.extract(html, base_url="https://coderprog.com")
        return json_data

    except ValueError:
        print("invalid data")
        return None


# argument is the output of html_to_json
def parse_item_metadata(json_data):
    item_list = []
    try:
        data = json_data.get("coderprog_page", [])
        for i in data:
            attribs = i.get("item_attribs")
            item = (
                parse_book_metadata(i)
                if ("PDF" in attribs or "EPUB" in attribs)
                else parse_course_metadata(i)
            )
            item_list.append(item)
        return item_list  # return a list
    except:
        print("[-] Parsing of metadata failed.")
    return None


def scrape(url: str) -> dict:
    """Scrape a website and return the scraped data.

    Args:
        url: The URL of the website to scrape.

    Returns:
        A dictionary containing the scraped data.

    """
    contents = get_response(url)
    print("[+] Scraping : {}".format(url))
    if not contents:
        print("Failed to fetch the page, please check the HTTP Status code")
        return None
    raw_json = html_to_json(contents)
    return parse_item_metadata(raw_json)


def single_site_scrape_test(url: str, dumpfile: str) -> None:
    """Scrape a website and save the scraped data to a file.

    Args:
        url: The URL of the website to scrape.
        dumpfile: The file to save the scraped data to.

    """
    # Scrape the site
    result = scrape(url)

    # s Save the scraped data to a file
    save_json(dumpfile, result)
    return


@click.command()
@click.option(
    "-n", "--num_pages", default=5, help="Pages from starting page, default : 5 pages"
)
@click.option(
    "-m", "--max_workers", default=3, help="Worker threads to run, default: 3 workers"
)
@click.option(
    "-s", "--sleep_time", default=7, help="Seconds to sleep, default: 7 seconds"
)
@click.option(
    "-p", "--when_pause", default=5, help="Pause time (defaults to every 5 MOD)"
)
@click.option(
    "-d", "--json_file", default="scraped_data.json", help="Filename output file"
)
# supports multi threaded parallel scraping
def start_scrape(
    num_pages: int, max_workers: int, json_file: str, sleep_time: float, when_pause: int
) -> None:
    """Starts a parallel scraping process.

    Args:
        num_pages: The number of pages to scrape.
        max_workers: The maximum number of workers to use.
        json_file: The file to save the scraped data to.
        sleep_time: The time to sleep between each scrape.
        when_pause: The number of pages to scrape before pausing.

    Returns:
        None.

    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        counter = 0
        scrape_futures = []
        list_of_pages = []
        for url in _link_generator(num_pages):
            scrape_futures.append(executor.submit(scrape, url))
            counter += 1
            if counter % when_pause == 0:
                time.sleep(sleep_time)
        # Iterate over the completed futures
        for future in concurrent.futures.as_completed(scrape_futures):
            try:
                # Get the result of the completed future
                if future.done() and not future.cancelled():
                    result = future.result()
                    list_of_pages.append(result)
            except Exception as e:
                print(f"(start_scrape) : An error occurred: {str(e)}")

    # list containing list of scraped pages
    save_json(json_file, list_of_pages)
    return


if __name__ == "__main__":
    start_scrape()
    #  single_site_scrape_test("https://coderprog.com", "__output__.json")
