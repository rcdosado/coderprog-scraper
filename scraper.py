import os
import click
import datetime

import time
import requests
import json
import threading

import re

from selectorlib import selectorlib
from selectorlib import formatter
from parsers.book_parser import parse_book
from parsers.course_parser import parse_course

ROOT_URL = "https://coderprog.com"

import concurrent.futures


def read_file_content(filename):
    cur_dir = os.path.dirname(__file__)
    with open(os.path.join(cur_dir, "tests", "data", filename)) as fileobj:
        content = fileobj.read()
    return content


def save_text(fn, contents):
    with open(fn, "w") as pf:
        pf.write(contents)
    return 0


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


def _splitter(data):
    return [i.strip() for i in data.split("|")]


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


def transform(json_data):
    item_list = []
    try:
        data = json_data.get("coderprog_page", [])
        for i in data:
            attribs = i.get("item_attribs")
            item = (
                parse_book(i)
                if ("PDF" in attribs or "EPUB" in attribs)
                else parse_course(i)
            )
            item_list.append(item)
        return item_list  # return a list
    except:
        print("Some error has occurred.")
    return None


def scrape(url):
    contents = get_response(url)
    print("attempt scraping : {}".format(url))
    if not contents:
        print("Failed to fetch the page, please check the HTTP Status code")
        return None
    return transform(html_to_json(contents))


def scrape_test(url):
    response = read_file_content("sample_index_page.html")
    jsf = html_to_json(response)
    ts = transform(jsf)
    return ts


class FileHandler:
    def __init__(self, filename):
        self.filename = filename
        self.lock = threading.Lock()

    def add_opening_bracket(self):
        self.write("[\n")

    def locked_file_dump(self, contents):
        try:
            with self.lock:
                with open(self.filename, "a") as file_writer:
                    for item in contents:
                        file_writer.write(json.dumps(item, indent=2) + ",\n")
                    file_writer.flush()
        except Exception as e:
            # Handle any exceptions that occurred during scraping
            print(f"An error occurred: {str(e)}")
        return

    def write(self, data):
        with open(self.filename, "a") as file_writer:
            file_writer.write(data)

    def add_closing_bracket(self):
        with open(self.filename, "r+") as file:
            file.seek(0, 2)
            file.seek(file.tell() - 3, 0)
            file.truncate()
            file.write("\n]")


@click.command()
@click.option(
    "-n", "--num_pages", default=5, help="Pages from starting page, default : 5 pages"
)
@click.option(
    "-m","--max_workers", default=3, help="Worker threads to run, default: 3 workers"
)
@click.option("-s", "--sleep_time", default=7, help="Seconds to sleep, default: 7 seconds")
@click.option("-p", "--when_pause", default=5, help="Pause time (defaults to every 5 MOD)")
@click.option(
    "-d",
    "--dump_file",
    default="scraped_data.json",
    help="Filename output file",
)
def start_scrape(num_pages, max_workers, dump_file, sleep_time, when_pause):
    file_handler = FileHandler(dump_file)
    file_handler.add_opening_bracket()
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        counter = 0
        scrape_futures = []
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
                    file_handler.locked_file_dump(result)
            except Exception as e:
                # Handle any exceptions that occurred during scraping
                print(f"(start_scrape) : An error occurred: {str(e)}")
    file_handler.add_closing_bracket()


if __name__ == "__main__":
    start_scrape()
    #  scrape_test(ROOT_URL);
