import os
import pytest

from selectorlib import selectorlib, formatter
from parsers.utils import read_file_content, read_json_file, save_json

from scraper import select_html_to_json, scrape


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
def with_thumbnail():
    return read_json_file("added_thumbnail_data.json")


def test_selector_if_returning_thumbnail_value(index_page_raw_html, with_thumbnail):
    formatters = formatter.Formatter.get_all()
    selector_text = """
    coderprog_page:
        css: article.latestPost.excerpt
        multiple: true
        type: Text
        children:
            item_thumbnail:
                css: article.latestPost img.aligncenter
                type: Image
            item_url:
                css: h2>a
                type: Link
            item_title:
                css: h2.title
                type: Text
            item_post_date:
                css: 'span.thetime span'
                type: Text
            item_attribs:
                css: p
                type: Text
    """
    extractor = selectorlib.Extractor.from_yaml_string(
        selector_text, formatters=formatters
    )
    expected_data = with_thumbnail
    json_data = extractor.extract(index_page_raw_html, base_url="https://coderprog.com")

    assert json_data == expected_data


def test_select_html_to_json_if_it_can_return_10_items_correctly(index_page_raw_html):
    raw_json = select_html_to_json(index_page_raw_html)
    result = raw_json.get("coderprog_page")
    assert len(result) == 10


# mock the HTTP get request, to respect the site
def test_scraper_function_returning_valid_json(
    mocker, index_page_raw_html, expected_json_data
):
    mocker.patch("scraper.get_response", return_value=index_page_raw_html)
    scraped_json_data = scrape("http://coderprog.com")

    scraped_size = len(scraped_json_data)
    expected_size = len(expected_json_data)

    #  test if they have the same number of entries
    assert scraped_size == expected_size

    # test if they have the same first item
    assert scraped_json_data[0] == expected_json_data[0]

    # test if they have the same last item
    assert scraped_json_data[scraped_size - 1] == expected_json_data[expected_size - 1]
