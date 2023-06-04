import os
import pytest
import yaml
import json


from selectorlib import selectorlib
from selectorlib import formatter
from selectorlib import cli

from parsers.book_parser import parse_book_metadata
from parsers.course_parser import parse_course_metadata
from parsers.utils import read_file_content, read_json_file, save_json

from scraper import html_to_json, scrape


@pytest.fixture
def index_page_raw_html():
    return read_file_content("sample_index_page.html")


@pytest.fixture
def succeeding_page():
    return read_file_content("sample_succeeding_page.html")


@pytest.fixture
def index_page_json_extract():
    return read_json_file("index_page_json_extract.json")


@pytest.fixture
def expected_json_data():
    return read_json_file("index_page_attrib_raw_json.json")


@pytest.fixture
def input_yaml():
    return read_file_content("input.yml")


@pytest.fixture
def output_yaml():
    return read_file_content("output.yml")


def test_html_to_json_if_it_can_return_10_items_correctly(index_page_raw_html):
    raw_json = html_to_json(index_page_raw_html)
    result = raw_json.get("coderprog_page")
    assert len(result) == 10


def test_scraper_function_returning_valid_json(
    mocker, index_page_raw_html, expected_json_data
):
    mocker.patch("scraper.get_response", return_value=index_page_raw_html)
    scraped_json_data = scrape("http://coderprog.com")
    assert scraped_json_data == expected_json_data
