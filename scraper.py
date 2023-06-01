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

ROOT_URL = "https://coderprog.com"

import concurrent.futures


def read_file_content(filename):
    cur_dir = os.path.dirname(__file__)
    with open(os.path.join(cur_dir, "tests", "data", filename)) as fileobj:
        content = fileobj.read()
    return content


def save_to_file(response):
    # saving response to `response.html`
    with open("response.html", "w") as fp:
        fp.write(response.text)


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


def _extract_values_from_patterns(patterns, json_string):
    # Extract values using regex patterns
    values = {}
    match = None
    for key, pattern in patterns.items():
        match = re.search(pattern, json_string)
        if match:
            values[key] = match.group(1)
    return values


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
        #  save_to_file(response)
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


def parse_book(json_data):
    title = json_data.get("item_title")
    url = json_data.get("item_url")
    post_date = json_data.get("item_post_date")

    # Define regex patterns for each value
    patterns = {
        "language": r"(\w+)",
        "year": r"(\d{4})",
        "ISBN": r"ISBN: ([\d-]+)",
        "pages": r"(\d+) Pages",
        "formats": r"(PDF|EPUB|PDF,EPUB|EPUB,PDF)",
        "size": r"(\d+ MB)",
    }

    # Extract values using regex patterns
    values = _extract_values_from_patterns(patterns, json_data.get("item_attribs"))

    language = values.get("language")
    year = values.get("year")
    isbn = values.get("ISBN")
    pages = values.get("pages")
    formats = values.get("formats")
    size = values.get("size")

    return {
        "category": "books",
        "title": title,
        "url": url,
        "posted": post_date,
        "language": language,
        "published": year,
        "isbn": isbn,
        "num_pages": pages,
        "types_available": formats,
        "size": size,
    }


def parse_tutorial(json_data):
    title = json_data.get("item_title")
    url = json_data.get("item_url")
    posted = json_data.get("item_post_date")

    # Define regex patterns for each value
    patterns = {
        "language": r"(\w+)",
        "format": r"(MP4|MKV|MP4,MKV|MP4,MKV)",
        "resolution": r"(AVC \w+.\w+)",
        "audio": r"(AAC \w+.\w+)",
        "duration": r"\|([^|]+(?i:lectures|lessons)[^|]+)\|",
        "size": r"(\d+(?:\.\d+)? [GM]B)",
    }

    # Extract values using regex patterns
    values = _extract_values_from_patterns(patterns, json_data.get("item_attribs"))

    language = values.get("language")
    file_type = values.get("format")
    resolution = values.get("resolution")
    audio = values.get("audio")
    duration = values.get("duration").strip() if (values.get("duration")) else "None"
    size = values.get("size")

    return {
        "category": "tutorial",
        "title": title,
        "url": url,
        "posted": posted,
        "language": language,
        "file_type": file_type,
        "resolution": resolution,
        "audio": audio,
        "duration": duration,
        "size": size,
    }


def sort_based_on_timestamp(dict_list):
    return sorted(dict_list, key=lambda x: x["timestamp"])


def transform(json_data):
    item_list = []
    try:
        data = json_data.get("coderprog_page", [])
        for i in data:
            attribs = i.get("item_attribs")
            item = (
                parse_book(i)
                if ("PDF" in attribs or "EPUB" in attribs)
                else parse_tutorial(i)
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
    response = read_file_content("sample_index_page2.html")
    return transform(html_to_json(response))


def locked_file_dump(handle, contents, lock):
    try:
        with lock:
            for item in contents:
                handle.write(json.dumps(item) + ",\n")
            handle.flush()
    except Exception as e:
        # Handle any exceptions that occurred during scraping
        print(f"An error occurred: {str(e)}")
    return


@click.command()
@click.option(
    "--num_pages", default=5, help="Pages from starting page, default : 5 pages"
)
@click.option(
    "--max_workers", default=3, help="Worker threads to run, default: 3 workers"
)
@click.option("--sleep_time", default=7, help="Seconds to sleep, default: 7 seconds")
@click.option("--when_pause", default=5, help="Pause time (defaults to every 5 MOD)")
@click.option(
    "--dump_file",
    default="scraped_data.json",
    help="Filename output file",
)
def start_scrape(num_pages, max_workers, dump_file, sleep_time, when_pause):
    lock = threading.Lock()
    with open(dump_file, "a") as file_writer:
        file_writer.write("[")
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
                        locked_file_dump(file_writer, result, lock)
                except Exception as e:
                    # Handle any exceptions that occurred during scraping
                    print(f"(start_scrape) : An error occurred: {str(e)}")
    with open(dump_file, "r+") as f:
        f.seek(0, 2)
        f.seek(f.tell() - 3, 0)
        f.truncate()
        f.write("\n]")


if __name__ == "__main__":
    start_scrape()
