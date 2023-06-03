import os
import pytest
import yaml
import json


from selectorlib import selectorlib
from selectorlib import formatter
from selectorlib import cli

from parsers.book_parser import parse_book_metadata
from parsers.course_parser import parse_course_metadata
from parsers.utils import read_file_content

from scraper import html_to_json


@pytest.fixture
def index_page():
    return read_file_content("sample_index_page.html")


@pytest.fixture
def succeeding_page():
    return read_file_content("sample_succeeding_page.html")


@pytest.fixture
def index_page_json_extract():
    json_extract = json.load("index_page_json_extract.json")
    return json_extract


@pytest.fixture
def input_yaml():
    return read_file_content("input.yml")


@pytest.fixture
def output_yaml():
    return read_file_content("output.yml")


def test_html_to_json_if_can_return_html_to_json_correctly(index_page):
    raw_json = html_to_json(index_page)
    result = raw_json.get("coderprog_page")
    assert len(result) == 10
