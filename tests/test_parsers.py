import pytest
import json

from parsers.course_parser import course_pattern
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
    raw = read_file_content("added_thumbnail_data.json")
    return json.loads(raw)


def test_parse_book_metadata_getting_first_entry(attrib_json_object):
    real_content = attrib_json_object["coderprog_page"]
    first_entry = real_content[0]
    result_json = parse_book_metadata(first_entry)
    expected_json_first = {
        "category": "books",
        "title": "Geometry for Programmers",
        "url": "https://coderprog.com/geometry-programmers-kaleniuk/",
        "thumbnail": "https://coderprog.com/wp-content/uploads/geometry-programmers-kaleniuk.jpg",
        "posted": "May 28, 2023",
        "language": "English",
        "published": "2023",
        "isbn": "978-1633439603",
        "num_pages": "440",
        "types_available": "PDF",
        "size": "54 MB",
    }
    assert result_json == expected_json_first

    json_size = len(real_content)

    last_entry = real_content[json_size - 1]
    result_json = parse_book_metadata(last_entry)
    expected_json_second = {
        "category": "books",
        "title": "Applications of Machine Learning in Digital Healthcare",
        "url": "https://coderprog.com/applications-ml-digital-healthcare/",
        "thumbnail": "https://coderprog.com/wp-content/uploads/applications-ml-digital-healthcare.jpg",
        "posted": "May 28, 2023",
        "language": "English",
        "published": "2023",
        "isbn": "978-1839533358",
        "num_pages": "418",
        "types_available": "PDF",
        "size": "33 MB",
    }
    assert result_json == expected_json_second


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
