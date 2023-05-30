import os
import time
import requests
import json
import jsonlines

import re

from selectorlib import selectorlib
from selectorlib import formatter

ROOT_URL = "https://coderprog.com"
SCRAPE_FILE = "scraped_data.json"


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
    response = requests.get(url, verify=False, headers=get_headers())
    if response.status_code != 200:
        print("ERROR {}: ".format(response.status_code))
        exit(-1)
    else:
        #  save_to_file(response)
        return response


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
        "book_title": title,
        "book_url": url,
        "book_posted": post_date,
        "book_language": language,
        "book_published": year,
        "book_isbn": isbn,
        "book_num_pages": pages,
        "book_types_available": formats,
        "book_size": size,
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
        "tutorial_title": title,
        "tutorial_url": url,
        "tutorial_posted": posted,
        "tutorial_language": language,
        "tutorial_file_type": file_type,
        "tutorial_resolution": resolution,
        "tutorial_audio": audio,
        "tutorial_duration": duration,
        "tutorial_size": size,
    }


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
        return item_list
    except:
        print("Some error has occurred.")
    return None


def insert_to_json(data, filename):
    with open(filename, "r") as file:
        json_data = json.load(file)
    json_data.append(data)
    with open(filename, "w") as file:
        json.dump(json_data, file)


def scrape(url):
    response = get_response(url)
    if not response:
        print(
            "Failed to fetch the page, please check `response.html` to see the response received from coderprog.com."
        )
        return None
    return transform(html_to_json(response.text))


def scrape_test(url):
    response = read_file_content("sample_index_page2.html")
    return transform(html_to_json(response))


if __name__ == "__main__":
    counter = 0
    save_text(SCRAPE_FILE, "[]")
    for url in _link_generator(9):
        print("[+] scraping : {}".format(url))
        insert_to_json(scrape(url), SCRAPE_FILE)
        counter=counter+1
        if counter % 5 == 0:
            print("[+] Sleeping for {} seconds".format(10))
            time.sleep(10)
