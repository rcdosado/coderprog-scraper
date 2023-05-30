import os
import pytest
import yaml
import json


from selectorlib import selectorlib
from selectorlib import formatter
from selectorlib import cli


def read_file_content(filename):
    cur_dir = os.path.dirname(__file__)
    with open(os.path.join(cur_dir, "data", filename)) as fileobj:
        content = fileobj.read()
    return content


@pytest.fixture
def html():
    return read_file_content("sample_index_page.html")


@pytest.fixture
def input_yaml():
    return read_file_content("input.yml")


@pytest.fixture
def output_yaml():
    return read_file_content("output.yml")

def test_content(html, input_yaml, output_yaml):
    base_url = "https://coderprog.com"
    formatters = formatter.Formatter.get_all()
    extractor = selectorlib.Extractor.from_yaml_string(
        input_yaml, formatters=formatters
    )
    output = extractor.extract(html, base_url=base_url)
    expected = yaml.safe_load(output_yaml)

    assert output['coderprog_page'][0]['item_title'] == expected['coderprog_page'][0]['item_title']

def test_json_string():
    assert {"test":"1234", "test2":"5678"} == {"test":"1234", "test2":"5678"}


