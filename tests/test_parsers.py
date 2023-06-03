import pytest
import os
import json

from parsers.course_parser import parse_course_metadata, course_pattern
from parsers.utils import _extract_values_from_patterns, read_file_content
from parsers.book_parser import parse_book_metadata, book_pattern


@pytest.fixture
def course_attrib():
    c = read_file_content("sample_course_attrib.txt")
    return c.encode("utf-8").decode("utf-8")


@pytest.fixture
def book_attrib():
    return read_file_content("sample_book_attrib.txt")


@pytest.fixture
def attrib_json_object():
    raw = read_file_content("index_page_attrib_raw_json.json")
    return json.loads(raw)


def test_parse_book_metadata_getting_first_entry(attrib_json_object):
    first_entry = attrib_json_object[0]

    result_json = parse_book_metadata(first_entry)
    expected_json_first = {
        "category": "books",
        "title": "Geometry for Programmers",
        "url": "https://coderprog.com/geometry-programmers-kaleniuk/",
        "posted": "May 28, 2023",
        "language": "English",
        "published": "2023",
        "isbn": "978-1633439603",
        "num_pages": "440",
        "types_available": "PDF",
        "size": "54 MB",
    }
    assert result_json == expected_json_first

    last_entry = attrib_json_object[-1]
    result_json = parse_book_metadata(last_entry)
    expected_json_second = {
        "category": "books",
        "title": "Applications of Machine Learning in Digital Healthcare",
        "url": "https://coderprog.com/applications-ml-digital-healthcare/",
        "posted": "May 28, 2023",
        "language": "English",
        "published": "2023",
        "isbn": "978-1839533358",
        "num_pages": "418",
        "types_available": "PDF",
        "size": "33 MB",
    }
    assert result_json == expected_json_second


#
def test_parse_course_metadata_correctly_parses_course_item(attrib_json_object):
    course_entry = attrib_json_object[1]
    result_json = parse_course_metadata(course_entry)
    expected_json = {
        "category": "tutorial",
        "title": "Unreal Engine 5 Action Adventure: Make Video Games",
        "url": "https://coderprog.com/unreal-engine-5-action-adventure/",
        "posted": "May 28, 2023",
        "language": "English",
        "file_type": "MP4",
        "resolution": "AVC 1280x720",
        "audio": "AAC 44KHz 2ch",
        "duration": "40 lectures (5h 12m)",
        "size": "4.23 GB",
    }
    assert result_json == expected_json


def test_extract_values_from_patterns_correctly_to_parse_book_meta(book_attrib):
    result_json = _extract_values_from_patterns(book_pattern, book_attrib)
    expect_json = {
        "language": "English",
        "year": "2023",
        "ISBN": "978-1633439603",
        "pages": "440",
        "formats": "PDF",
        "size": "54 MB",
    }
    assert result_json == expect_json


def test_extract_values_from_patterns_correctly_to_parse_course_meta(course_attrib):
    result_json = _extract_values_from_patterns(course_pattern, course_attrib)
    expect_json = {
        "language": "English",
        "format": "MP4",
        "resolution": "AVC 1280Ã—720",
        "audio": "AAC 44KHz 2ch",
        "duration": " 83 lectures (8h 51m) ",
        "size": "2.92 GB",
    }
    assert result_json == expect_json


#
#
#
